#!/usr/bin/perl

require "/usr/local/bin/openVpnFiles/mysqlFunctions.pm";
require "/usr/local/bin/openVpnFiles/dateMailFunctions.pl";


my $handle; my $textLog; my $remoteIp; my $localIp; my $clientName;
my @tempText; my $temp; my @secTemp; my %hashvars = ();
my $mysqlConn; my $mysqlError; my $query; my $datetime;
my $date; my $time; my $mysqlHash; my $mainId; my $rootQdisc; my $result;
###################################################################################################
my $envText = `env`;
@tempText = split('\n',$envText); 
open($handle,">>","/usr/local/bin/openVpnFiles/openVPNLog.log");
$date = GetData();
$time = GetTime();
foreach $temp (@tempText)
{
	if($temp =~ "common_name" or $temp =~ "ifconfig_pool_remote_ip" or $temp =~ "ifconfig_pool_local_ip" or $temp =~ "trusted_ip" or $temp =~ "bytes_sent" or $temp =~ "bytes_received" or $temp =~ "time_duration")
	{
		$temp =~ s/\n//g;
		@secTemp = split('=',$temp);
		$hashvars{$secTemp[0]} = $secTemp[1];
		$textLog = "$secTemp[0]=$secTemp[1] \n";
#		print $handle $textLog;
	}
}
$textLog = "[$time $date][disconnectScript] #########################################\n";
print $handle $textLog;
$mysqlConn = MysqlConnection->new();
$mysqlError = $mysqlConn->StartConnection();
$query = "select id from connextions where common_name='$hashvars{common_name}' and time_stop is null order by time_start desc limit 1";
$mysqlConn->SetMakeQuery($query);
$mysqlHash = $mysqlConn->GetHashrow();
$mysqlConn->EndQuery();
$mainId = $mysqlHash->{id};
$query = "update connextions set time_stop='$date $time',bytes_sent='$hashvars{bytes_sent}',bytes_received='$hashvars{bytes_received}',time_duration='$hashvars{time_duration}' where id='$mainId'";
$mysqlConn->SetMakeQuery($query);
$mysqlConn->EndQuery();
$query = "select id from users where common_name='$hashvars{common_name}'";
$mysqlConn->SetMakeQuery($query);
$mysqlHash = $mysqlConn->GetHashrow();
$mysqlConn->EndQuery();
$rootQdisc = $mysqlHash->{id};
RemoveDownloadQos();
RemoveUploadQos();
##############################################
$command = "/sbin/iptables -t mangle -D PREROUTING -i tun0 -s ".$hashvars{ifconfig_pool_remote_ip}." -j MARK --set-mark ".$mysqlHash->{id};
print $handle "[$time $date][disconnectScript] $command\n";
$result = `$command`;
$result = "[$time $date][disconnectScript] DEL from iptables result: $result \n";
print $handle $result;
$mysqlConn->StopConnection();
close($handle);
###################################################################################################

sub RemoveUploadQos
{
	my $qdiscHandle; my $command; my $result;
	$qdiscHandle = $rootQdisc * 10;
	$command = "/sbin/tc filter del dev eth0 protocol ip parent 1:0 prio 1000 handle $rootQdisc fw flowid 1:$rootQdisc";	
	print $handle "[$time $date][disconnectScript] $command \n";
	$result = `$command`;
	$result = "[$time $date][disconnectScript] DEL filter cmd response = $result\n";
	print $handle $result;
	$command = "/sbin/tc qdisc del dev eth0 parent 1:$rootQdisc handle $qdiscHandle: sfq perturb 10";
	print $handle "[$time $date][disconnectScript] $command \n";
	$result = `$command`;
	$result = "[$time $date][disconnectScript] DEL qdisc cmd response = $result\n";
	print $handle $result;
	$command = "/sbin/tc class del dev eth0 parent 1:2 classid 1:$rootQdisc";
	print $handle "[$time $date][disconnectScript] $command \n";
	$result = `$command`;
	$result = "[$time $date][disconnectScript] DEL class cmd response = $result\n";
	print $handle $result;
}

sub RemoveDownloadQos
{
	my $command; my $result; my $qdiscHandle;
	$qdiscHandle = $rootQdisc * 10;
	$command = "/sbin/tc filter del dev tun0 protocol ip parent 1:0 handle 800::$rootQdisc prio 1000 u32 match ip dst ".$hashvars{ifconfig_pool_remote_ip}." flowid 1:".$rootQdisc;
	print $handle "[$time $date][disconnectScript] $command \n";
	$result = `$command`;
	$result = "[$time $date][disconnectScript] DEL filter cmd response = $result\n";
	print $handle $result;
	$command = "/sbin/tc qdisc del dev tun0 parent 1:$rootQdisc handle $qdiscHandle: sfq perturb 10 ";
	print $handle "[$time $date][disconnectScript] $command \n";
	$result = `$command`;
	$result = "[$time $date][disconnectScript] DEL qdisc cmd response = $result\n";
	print $handle $result;
	$command = "/sbin/tc class del dev tun0 parent 1:2 classid 1:$rootQdisc";
	print $handle "[$time $date][disconnectScript] $command \n";
	$result = `$command`;
	$result = "[$time $date][disconnectScript] DEL class cmd response = $result\n";
	print $handle $result;
}
