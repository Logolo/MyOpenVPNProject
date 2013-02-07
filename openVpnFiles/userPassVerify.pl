#!/usr/bin/perl 

use Digest::MD5;
use lib "/usr/local/bin/openVpnFiles";
use mysqlFunctions;


my $fileName = $ARGV[0];
my $logText; my $temp; my $user; my $pass; my $text; my $digestPass; my $mysqlError; my $trueDigestPass;
my @tempText; my $handle; my $authFileHandle; my $md5; my $mysqlConn; my $query; my $hashrow; 
open($handle,">>","/usr/local/bin/openVpnFiles/openVPNLog.log");
#######################################################################
$mysqlConn = MysqlConnection->new();
$mysqlError = $mysqlConn->StartConnection();
if($mysqlError == 10)
{
	$logText = "Mysql connection NOT OK...\n";
	print $handle $logText;
	close($handle);
	$mysqlConn->StopConnection();
	exit 1;
}
#exit 0;
#$logText = "Temp file for auth = $fileName\n";
#print $handle $logText;
if(!$fileName)
{
	$logText = "Temp file for auth is not OK\n";
	print $handle $logText;
	close($handle);
	$mysqlConn->StopConnection();
	exit 1;
}
open($authFileHandle,$fileName);
if(!$authFileHandle)
{
	$logText = "Unable to open auth temp file.\n";
	print $handle $logText;
        close($handle);
        $mysqlConn->StopConnection();
	exit 1;
}
$user = <$authFileHandle>;
$user =~ s/\n//g;
$pass = <$authFileHandle>;
$pass =~ s/\n//g;
if(!$user)
{
	$logText = "Username not send from user...\n";
	print $handle $logText;
        close($handle);
        close($authFileHandle);
        $mysqlConn->StopConnection();
	exit 1;
}
if(!$pass)
{
	$logText = "Password not send from user...\n";
	print $handle $logText;
        close($handle);
        close($authFileHandle);
        $mysqlConn->StopConnection();
	exit 1;
}
$md5 = Digest::MD5->new;
$md5->add("$user $pass");
$digestPass = $md5->hexdigest;
$query = "select password from users where username='$user'";
$mysqlConn->SetMakeQuery($query);
$hashrow = $mysqlConn->GetHashrow();
$mysqlConn->EndQuery();
$trueDigestPass = $hashrow->{password};
if(!$trueDigestPass)
{
	$logText = "No password was set for this user: $user\n";
	print $handle $logText;
        close($handle);
        close($authFileHandle);
        $mysqlConn->StopConnection();
	exit 1;
}
if($trueDigestPass ne $digestPass)
{
	$logText = "Password do not match for user: $user \n";
	print $handle $logText;
        close($handle);
        close($authFileHandle);
        $mysqlConn->StopConnection();
	exit 1;
}
$logText = "Authentification success for user $user \n";
print $handle $logText;
#######################################################################
close($handle);
close($authFileHandle);
$mysqlConn->StopConnection();
exit 0;
