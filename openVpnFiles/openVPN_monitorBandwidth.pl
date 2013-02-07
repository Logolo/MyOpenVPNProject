#!/usr/bin/perl

require "/usr/local/bin/openVpnFiles/mysqlFunctions.pm";
require "/usr/local/bin/openVpnFiles/dateMailFunctions.pl";



my $handle; my $option; my $file = "monitorLog.txt";
my $date; my $time; my %unitHash = ("bit" => "1", "Kbit" => "1024", "Mbit" => "1048576");
my $mysqlConn; my $mysqlError; my $mysqlHash; my $query; my $userId; my $downRateKbit; my $upRateKbit; 
my $count; my $username; my $downRate; my $upRate; my %parameters = ();
###########################################################
$mysqlConn = MysqlConnection->new();
$mysqlError = $mysqlConn->StartConnection();
open($handle, ">>", "$file");
if(!$handle)
{
	print "Unable to open log file\n";
	exit(0);
}
$date = GetData();
$time = GetTime();
$logText = "#####################################################\n";
$logText .= "Start $date $time\n";
print $handle $logText;
if($mysqlError == 10)
{
	$logText = "--MysqlConnection NOT OK\nEnd..................\n";
	print $handle $logText;
	exit(0);
}
if(!$ARGV[0]) {$option = "L";} ## input in the log file and insert in mysql monitorBandwidth
elsif($ARGV[0] eq "-R") {$option = "R";} ## real time monitor ... no logs ... no mysql
else
{
	$logText = "Option unrecognized\nEnd..................\n";
	print $handle $logText;	
	exit(0);
}
if($option eq "R")
{
	$logText = "--option real time chosen ... implicit interval 1 second\n";
	print $handle $logText;
	$count = 0; ## max count is 1000 loops
	do
	{
		$count++;
		$query = "select distinct u.id,u.username from connextions c,users u where c.time_stop is null and u.username=c.username";
		$mysqlConn->SetMakeQuery($query);
		while($mysqlHash = $mysqlConn->GetHashrow())
		{
			$userId = $mysqlHash->{id};
			$username = $mysqlHash->{username};
			print "Rate Report for $username\n";
			$parameters{userId} = $userId;
			GetDownloadBandwidth(\%parameters);	
			GetUploadBandwidth(\%parameters);
			$downRate = $parameters{downRate}*$parameters{downUnit};
			$upRate = $parameters{upRate}*$parameters{upUnit};
			$downRateKbit = $downRate / 1024;
			$downRateKbit = int($downRateKbit);
			$upRateKbit = $upRate / 1024;
			$upRateKbit = int($upRateKbit);
			print "Download = $downRate bits ($downRateKbit Kbits)\n";
			print "Upload = $upRate bits ($upRateKbit Kbits)\n";
			print "----------------\n";
		}
		$mysqlConn->EndQuery();
		print "#######################################\n";
		sleep(3);
	}while($count < 1000);
}
elsif($option eq "L")
{
	$logText = "--option mysql chosen \n";
	print $handle $logText;
	$query = "select distinct u.id,u.username from connextions c,users u where c.time_stop is null and u.username=c.username";
	$mysqlConn->SetMakeQuery($query);
	while($mysqlHash = $mysqlConn->GetHashrow())
	{
		$userId = $mysqlHash->{id};
		$username = $mysqlHash->{username};
		$parameters{userId} = $userId;
		GetDownloadBandwidth(\%parameters);
		GetUploadBandwidth(\%parameters);
		$downRate = $parameters{downRate}*$parameters{downUnit};
		$upRate = $parameters{upRate}*$parameters{upUnit};
		$downRateKbit = $downRate / 1024;
		$downRateKbit = int($downRateKbit);
		$upRateKbit = $upRate / 1024;
		$upRateKbit = int($upRateKbit);
		$query = "insert into monitor_users values (null,'$userId','$downRateKbit','$upRateKbit','$date', '$time')";
		$mysqlConn->SetMakeQuerySecondary($query);
		$mysqlConn->EndQuerySecondary();
		$logText = "--user $userId connected\n";
		print $handle $logText;	
	}
	$mysqlConn->EndQuery();
}
$logText = "End................\n";
print $handle $logText;
close($handle);
$mysqlConn->StopConnection();
##########################################################
sub GetUploadBandwidth
{
	my $parameters = shift;
	my $command; my $result; my @resultLines; my $logText; my $line; my $search = 0; 
	my $rateUpload; my $unit; my $userId = $parameters->{userId};
	$command = "/sbin/tc -s class show dev eth0 | grep 'htb 1:$userId' -C 2";
	$result = `$command`;
	if(!$result)
	{
		$logText = "--tc command returned NULL\nEnd................\n";
		print $handle $logText;
		exit(0);
	}
	@resultLines = split('\n',$result);
	foreach $line (@resultLines)
	{
		$line =~ s/\n//g;
		if($line =~ "class htb 1:$userId") {$search = 1;} ## this is here just to be sure that I get the right stuff
		if($search == 1 and $line =~ "rate" and $line =~ "pps")
		{
			$logText = "--$line \n";
			print $handle $logText;
			@lineParts = split(' ',$line);
			$rateUpload = $lineParts[1];
			$rateUpload =~ s/[a-z]|[A-Z]//g;
			$unit = $lineParts[1];
			$unit =~ s/[0-9]//g;
			$unit = $unitHash{$unit};
			$parameters->{upUnit} = $unit;
			$parameters->{upRate} = $rateUpload;
			last;
		}
	}
}

sub GetDownloadBandwidth
{
	$parameters = shift;
	my $command; my $result; my @resultLines; my $logText; my $line; my $search = 0; 
	my $rateDownload; my $unit; my $userId = $parameters->{userId};
        $command = "/sbin/tc -s class show dev tun0 | grep 'htb 1:$userId' -C 2";
        $result = `$command`;
        if(!$result)
        {
                $logText = "--tc command returned NULL\nEnd................\n";
                print $handle $logText;
                exit(0);
        }
        @resultLines = split('\n',$result);
        foreach $line (@resultLines)
        {
                $line =~ s/\n//g;
                if($line =~ "class htb 1:$userId") {$search = 1;} ## this is here just to be sure that I get the right stuff
                if($search == 1 and $line =~ "rate" and $line =~ "pps")
                {
                        $logText = "--$line \n";
                        print $handle $logText;
                        @lineParts = split(' ',$line);
                        $rateDownload = $lineParts[1];
                        $rateDownload =~ s/[a-z]|[A-Z]//g;
                        $unit = $lineParts[1];
                        $unit =~ s/[0-9]//g;
                        $unit = $unitHash{$unit};
			$parameters->{downUnit} = $unit;
			$parameters->{downRate} = $rateDownload;
			last;
                }
        }	
}
