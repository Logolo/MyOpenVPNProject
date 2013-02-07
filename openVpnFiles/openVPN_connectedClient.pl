#!/usr/bin/perl

require "/usr/local/bin/openVpnFiles/mysqlFunctions.pm";
require "/usr/local/bin/openVpnFiles/dateMailFunctions.pl";

my $handle; my $textLog; my $remoteIp; my $localIp; my $clientName;
my @tempText; my $temp; my @secTemp; my %hashvars = ();
my $mysqlConn; my $mysqlError; my $query; my $datetime;
my $date; my $time; my $mysqlHash; my $rootQdisc; my $command; my $resultText;
my $downMin; my $downMax; my $uploadMin; my $uploadMax; my $userId; my $userName;
###################################################################################################
my $envText = `env`;
@tempText = split('\n',$envText); 
open($handle,">>","/usr/local/bin/openVpnFiles/openVPNLog.log");
$date = GetData();
$time = GetTime();
foreach $temp (@tempText)
{
	if($temp =~ "common_name" or $temp =~ "ifconfig_pool_remote_ip" or $temp =~ "ifconfig_pool_local_ip" or $temp =~ "username" or $temp =~ "trusted_ip") 
	{
		@secTemp = split('=',$temp);
		$hashvars{$secTemp[0]} = $secTemp[1];
		$textLog = "[$time $date][connectScript] $secTemp[0]=$secTemp[1]\n";
#		print $handle $textLog;
	}
#	else 
#	{
#		@secTemp = split('=',$temp);
#		$textLog = "[$time $date][connectScript] $secTemp[0]=$secTemp[1] \n";
#		print $handle $textLog;
#	}
}
$textLog = "[$time $date][connectScript]#########################################\n";
print $handle $textLog;
$date = GetData();
$time = GetTime();
$mysqlConn = MysqlConnection->new();
$mysqlError = $mysqlConn->StartConnection();
$query = "select id,down_min,down_max,upload_max,upload_min,username from users where common_name='$hashvars{common_name}'";
$mysqlConn->SetMakeQuery($query);
$mysqlHash = $mysqlConn->GetHashrow();
$mysqlConn->EndQuery();
$downMin = $mysqlHash->{down_min};
$downMax = $mysqlHash->{down_max};
$uploadMax = $mysqlHash->{upload_max};
$uploadMin = $mysqlHash->{upload_min};
$userName = $mysqlHash->{username};
$userId = $mysqlHash->{id};
$query = "insert into connextions (remote_ip,remote_private_ip,username,common_name,time_start) values ('$hashvars{ifconfig_pool_remote_ip}','$hashvars{trusted_ip}','$userName','$hashvars{common_name}','$date $time')";
$mysqlConn->SetMakeQuery($query);
$mysqlConn->EndQuery();
$textLog = "[$time $date][connectScript] userId=$userId downMin=$downMin downMax=$downMax uploadMin=$uploadMin uploadMax=$uploadMax\n";
print $handle $textLog;
if($userId and $downMax and $downMin)
{
	$command = "/sbin/tc qdisc show dev tun0";
	$resultText = `$command`;
	$textLog = "[$time $date][connectScript] Inside qos decision\n[$time $date][connectScript] RES=$resultText\n";
	print $handle $textLog;
	$textLog = "[$time $date][connectScript] remoteIp=".$mysqlHash->{remote_ip}." -- ".$hashvars{ifconfig_pool_remote_ip}."\n";
	print $handle $textLog;
	if($resultText =~ "qdisc htb 1: " and $resultText =~ "default 1150") {DownloadQos();}
	else
	{
		$command = "/sbin/tc qdisc add dev tun0 root handle 1: htb default 1150";
		print $handle "[$time $date][connectScript] $command\n";
		system($command);
		$command = "/sbin/tc class add dev tun0 parent 1: classid 1:2 htb rate 20mbit ceil 20mbit";
		print $handle "[$time $date][connectScript] $command\n";
		system($command);
		$command = ""; ## adaugare garantare default
		DownloadQos();	
	}
}
if($userId and $uploadMax and $uploadMin)
{
	$command = "/sbin/iptables -t mangle -A PREROUTING -i tun0 -s ".$hashvars{ifconfig_pool_remote_ip}. " -j MARK --set-mark ".$mysqlHash->{id};
	print $handle "[$time $date][connectScript] $command\n";
	system($command);
	######################################
	$command = "/sbin/tc qdisc show dev eth0";
	$resultText = `$command`;
	if($resultText =~ "qdisc htb 1: " and $resultText =~ "default 1150") {UploadQos();}	
	else
	{
		$command = "/sbin/tc qdisc add dev eth0 root handle 1: htb default 1150";
		print $handle "[$time $date][connectScript] $command\n";
		system($command);
		$command = "/sbin/tc class add dev eth0 parent 1: classid 1:2 htb rate 20mbit ceil 20mbit";
		print $handle "[$time $date][connectScript] $command\n";
		system($command);
		$command = ""; ## adaugare garantare default
		UploadQos();
	}
}
$textLog = "[$time $date][connectScript]#########################################\n";
print $handle $textLog;
$mysqlConn->StopConnection();
close($handle);
###################################################################################################

sub UploadQos
{
	my $command; my $qdiscHandle;
	$qdiscHandle = $userId * 10;
	$command = "/sbin/tc class add dev eth0 parent 1:2 classid 1:$userId htb rate $uploadMin ceil $uploadMax";
	print $handle "[$time $date][connectScript] $command\n";
	system($command);
	$command = "/sbin/tc qdisc add dev eth0 parent 1:$userId handle $qdiscHandle: sfq perturb 10";
	print $handle "[$time $date][connectScript] $command\n";
	system($command);
	$command = "/sbin/tc filter add dev eth0 protocol ip parent 1:0 prio 1000 handle $userId fw flowid 1:$userId";
	print $handle "[$time $date][connectScript] $command\n";
	system($command);
}

sub DownloadQos
{
	my $command; my $qdiscHandle;
	$qdiscHandle = $userId * 10;
	$command = "/sbin/tc class add dev tun0 parent 1:2 classid 1:$userId htb rate $downMin ceil $downMax";
	print $handle "[$time $date][connectScript] $command\n";
	system($command);
	$command = "/sbin/tc qdisc add dev tun0 parent 1:$userId handle $qdiscHandle: sfq perturb 10";
	print $handle "[$time $date][connectScript] $command\n";
	system($command);
	$command = "/sbin/tc filter add dev tun0 protocol ip parent 1:0 handle 800::$userId prio 1000 u32 match ip dst ".$hashvars{ifconfig_pool_remote_ip}." flowid 1:$userId";
	print $handle "[$time $date][connectScript] $command\n";
	system($command);
}
