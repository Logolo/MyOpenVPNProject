#!/usr/bin/perl

require "/usr/local/bin/openVpnFiles/dateMailFunctions.pl";
use Cwd;

my $handle; my $textlog; my $commonName; my $date; my $time;
my $path = "/etc/openvpn/easy-rsa/2.0/"; my $result; my $command;
$commonName = $ARGV[0]; my $line; my @textParts; my $exportHandle;
#########################################################################################
open($handle,">>","/usr/local/bin/openVpnFiles/openVPNLog.log");
open($exportHandle,"/usr/local/bin/openVpnFiles/exportVarFile");
$date = GetData();
$time = GetTime();
$textlog = "[$date $time createCertificate] ##################################\n";
print $handle $textlog;
if(!$commonName)
{
	$textlog = "[$date $time createCertificate] Nu este setat commonName\n";
	print $handle $textlog;
}
$result = getcwd();
$textlog = "[$date $time createCertificate] currentDir = $result \n";
print $handle $textlog;
chdir("$path");
$result = getcwd();
$textlog = "[$date $time createCertificate] currentDir = $result \n";
print $handle $textlog;
while($line = <$exportHandle>)
{
	$line =~ s/\n//g;
	@textParts = split("=",$line);
	$ENV{$textParts[0]} = $textParts[1];
}
$command = "./pkitool $commonName";
$result = `$command`;
$textlog = "$result \n";
print $handle $textlog;
foreach $temp (keys %ENV)
{	
	$textlog = $temp;
	$textlog .= " = $ENV{$temp} \n";
	print $handle $textlog;
}
close($handle);
close($exportHandle);
#########################################################################################
