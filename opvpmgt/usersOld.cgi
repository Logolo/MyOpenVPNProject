#!/usr/bin/perl

use Digest::MD5;
use lib "modules";
use HtmlObject;
use mysqlFunctions;
use PostVars;
use Cwd;


my $htmlPage; my %params = (); my $otherHash; my $action; my $postVars;
my $mysqlConn; my $mysqlError; my $query; my $mysqlHash; my $userName; my $userId;
my $opvBinPath = "/usr/local/bin/openVpnFiles/";
my $opvEtcPath = "/etc/openvpn/";
my $opvKeyPath = "$opvEtcPath"."easy-rsa/2.0/keys/";
###############################################################################
$postVars = PostVars->new();
$htmlPage = HtmlObject->new();
%params = ("pageTitle" => "OpenVPN Mng", "cssStyle" => "style.css");
$htmlPage->StartPage(\%params);
$mysqlConn = MysqlConnection->new();
$mysqlError = $mysqlConn->StartConnection();
$action = $postVars->GetVarSingle("action");
if(!$action)
{
	%params = ("width" => "300", "align" => "left", "msg" => "Users Page. Add. Delete. Modify.", "class" => "headerTitleLeft");
	$htmlPage->Header(\%params);
	$htmlPage->ClearAll();
	$htmlPage->TheBR();
	ShowUsers();
}
elsif($action eq "addNewUser")
{
	my %selectValues = (); my %paramsSelect = (); my %paramsInput = ();
	my $userName = $postVars->GetVarSingle("userName");
	my $password = $postVars->GetVarSingle("password");
	my $commonName = $postVars->GetVarSingle("commonName");
	my $qosUpload = $postVars->GetVarSingle("qosUpload");
	my $qosDownload = $postVars->GetVarSingle("qosDownload");
	my $buildGraph = $postVars->GetVarSingle("buildGraph");
        %params = ("width" => "300", "align" => "left", "msg" => "...Add New User Page...", "class" => "headerTitleLeft");
        $htmlPage->Header(\%params);
        $htmlPage->ClearAll();
        $htmlPage->TheBR();
	%params = ("method" => "post", "name" => "userAddVerify");
	$htmlPage->StartForm(\%params);
        %params = ("width" => "300", "align" => "left", "cellpadding" => "1", "cellspacing" => "1");
        $htmlPage->StartTable(\%params);
	EditUsername($userName, "teste");
	EditPassword($password, "teste");
	EditCommonName($commonName, "teste");
	EditQosUpload($qosUpload, "headerLeft");
	EditQosDownload($qosDownload, "headerLeft");
	EditBuildGraph($buildGraph, "headerLeft");
	EditActiveUser($activeUser, "headerLeft");
	AddButton();
	$htmlPage->EndTable();
	%params = ("name" => "action", "value" => "addNewUserStepOne");
	$htmlPage->HiddenVar(\%params);
	$htmlPage->EndForm();
}
elsif($action eq "addNewUserStepOne")
{
	my %params = (); my $mysqlHash;
        my $userName = $postVars->GetVarSingle("userName");
        my $password = $postVars->GetVarSingle("password");
        my $commonName = $postVars->GetVarSingle("commonName");
        my $qosUpload = $postVars->GetVarSingle("qosUpload");
        my $qosDownload = $postVars->GetVarSingle("qosDownload");
        my $buildGraph = $postVars->GetVarSingle("buildGraph");
	my $activeUser = $postVars->GetVarSingle("activeUser");
	my $downMin; my $downMax; my $upMin; my $upMax; 
	my $duplicat = 1; ## no duplicates found => is OK
	my %yesNoHash = ("1" => "Y", "2" => "N"); my $md5; my $digestPass;
	$query = "select count(*) as count from users where username='$userName' or common_name='$commonName'";
	$mysqlConn->SetMakeQuery($query);
	$mysqlHash = $mysqlConn->GetHashrow();
	$mysqlConn->EndQuery();
	if($mysqlHash->{count} > 0) {$duplicat = 2;}
	if($userName and $password and $commonName and $qosUpload ne "---" and $qosDownload ne "---" and $buildGraph ne "---" and $activeUser ne "---" and $duplicat == 1)
	{
		$query = "select min,max from qos_limits where id='$qosDownload'";
		$mysqlConn->SetMakeQuery($query);
		$mysqlHash = $mysqlConn->GetHashrow();
		$mysqlConn->EndQuery();
		$downMin = $mysqlHash->{min};
		$downMax = $mysqlHash->{max};
		if(!$downMax) {$downMax = "NULL"; $downMin = "NULL";}
		else {$downMax = "'$downMax'"; $downMin = "'$downMin'";}
		$query = "select min,max from qos_limits where id='$qosUpload'";
		$mysqlConn->SetMakeQuery($query);
		$mysqlHash = $mysqlConn->GetHashrow();
		$mysqlConn->EndQuery();
		$upMax = $mysqlHash->{max};
		$upMin = $mysqlHash->{min};
		if(!$upMin) {$upMin = "NULL"; $upMax = "NULL";}
		else {$upMin = "'$upMin'"; $upMax = "'$upMax'";}
                $md5 = Digest::MD5->new;
                $md5->add("$userName $password");
                $digestPass = $md5->hexdigest;
		$query = "insert into users (username,password,common_name,certificate,active,down_min,down_max,upload_max,upload_min,graph_active) values ('$userName', '$digestPass', '$commonName', null, '$yesNoHash{$activeUser}', $downMin, $downMax, $upMax, $upMin, '$yesNoHash{$buildGraph}')";
		$mysqlConn->SetMakeQuery($query);
		$mysqlConn->EndQuery();
	        %params = ("width" => "300", "align" => "left", "msg" => "Users Page. Add. Delete. Modify.", "class" => "headerTitleLeft");
        	$htmlPage->Header(\%params);
	        $htmlPage->ClearAll();
        	$htmlPage->TheBR();
	        ShowUsers();
        	$htmlPage->TheBR();
		CreateUserCertificate($commonName);
	}
	else
	{
		%params = ("width" => "300", "align" => "left", "msg" => "...Add New User Page...", "class" => "headerTitleLeft");
		$htmlPage->Header(\%params);
		$htmlPage->ClearAll();
		$htmlPage->TheBR();
		%params = ("method" => "post", "name" => "userAddVerify");
	        $htmlPage->StartForm(\%params);
		%params = ("width" => "300", "align" => "left", "cellpadding" => "1", "cellspacing" => "1");	
		$htmlPage->StartTable(\%params);
		$style = "teste";
		if(!$userName or $duplicat == 2) {$style = "testeRed";}
		EditUsername($userName,$style);
		$style = "teste";
		if(!$password) {$style = "testeRed";}
		EditPassword($password,$style);
		$style = "teste";
		if(!$commonName) {$style = "testeRed";}
		EditCommonName($commonName, $style);
		$style = "normal";
		if($qosUpload eq "---") {$style = "normalRed";}
		EditQosUpload($qosUpload,$style);
		$style = "headerLeft";
		if($qosDownload eq "---") {$style = "normalRed";}
		EditQosDownload($qosDownload,$style);
		$style = "headerLeft";
		if(!$buildGraph or $buildGraph eq "---") {$style = "normalRed";} 
		EditBuildGraph($buildGraph,$style);
		$style = "headerLeft";
		if(!$activeUser or $activeUser eq "---") {$style = "normalRed";}
		EditActiveUser($activeUser,$style);
		AddButton();
		$htmlPage->EndTable();
		%params = ("name" => "action", "value" => "addNewUserStepOne");
		$htmlPage->HiddenVar(\%params);
		$htmlPage->EndForm();
		if($duplicat == 2)
		{
			$htmlPage->ClearAll();
			$htmlPage->TheBR();
			%params = ("width" => "300", "align" => "left", "msg" => "...Username is already used...", "class" => "headerTitleLeft");
			$htmlPage->Header(\%params);
			$htmlPage->TheBR();
		}
	}
}
elsif($action eq "editUser")
{
	my $curentUserId = $postVars->GetVarSingle("curentUserId");
	my $query; my $hashref; my $sechashref; my %yesnoHash = ("Y" => "1", "N" => "2");
        %params = ("width" => "300", "align" => "left", "msg" => "...Edit User Page...", "class" => "headerTitleLeft");
        $htmlPage->Header(\%params);
        $htmlPage->ClearAll();
        $htmlPage->TheBR();
	%params = ("width" => "900", "align" => "center", "cellpadding" => "1", "cellspacing" => "1");
	$htmlPage->StartTable(\%params);
	ShowUsersStartHeader();
	ShowCurrentUser($curentUserId);
	$htmlPage->EndTable();
	$htmlPage->TheBR();
	$query = "select * from users where id='$curentUserId'";
	$mysqlConn->SetMakeQuery($query);
	$hashref = $mysqlConn->GetHashrow();
	$mysqlConn->EndQuery();
	%params = ("width" => "300", "align" => "left", "cellpadding" => "1", "cellspacing" => "1");
        $htmlPage->StartTable(\%params);
	%params = ("name" => "editUserSave", "method" => "post", "target" => "down");
	$htmlPage->StartForm(\%params);
        EditUsername($hashref->{username}, "teste");
        EditPassword("anyText", "teste");
        EditCommonName($hashref->{common_name}, "teste");
	$query = "select id from qos_limits where min='$hashref->{upload_min}' and max='$hashref->{upload_max}'";
	$mysqlConn->SetMakeQuery($query);
	$sechashref = $mysqlConn->GetHashrow();
	$mysqlConn->EndQuery();
        EditQosUpload($sechashref->{id}, "headerLeft");
	$query = "select id from qos_limits where min='$hashref->{down_min}' and max='$hashref->{down_max}'";
	$mysqlConn->SetMakeQuery($query);
	$sechashref = $mysqlConn->GetHashrow();
	$mysqlConn->EndQuery();
        EditQosDownload($sechashref->{id}, "headerLeft");
        EditBuildGraph($yesnoHash{$hashref->{graph_active}}, "headerLeft");
        EditActiveUser($yesnoHash{$hashref->{active}}, "headerLeft");
        AddButton("Modify User");
	%params = ("name" => "action", "value" => "editUserSave");
	$htmlPage->HiddenVar(\%params);
	%params = ("name" => "curentUserId", "value" => "$curentUserId");
	$htmlPage->HiddenVar(\%params);
	$htmlPage->EndForm();
        $htmlPage->EndTable();
	
	
}
elsif($action eq "editUserSave")
{
	my $curentUserId = $postVars->GetVarSingle("curentUserId");
	my $userName = $postVars->GetVarSingle("userName");
	my $password = $postVars->GetVarSingle("password");
	my $commonName = $postVars->GetVarSingle("commonName");
	my $qosUpload = $postVars->GetVarSingle("qosUpload");
	my $qosDownload = $postVars->GetVarSingle("qosDownload");
	my $buildGraph = $postVars->GetVarSingle("buildGraph");
	my $activeUser = $postVars->GetVarSingle("activeUser");
        my $downMin; my $downMax; my $upMin; my $upMax; my $query; my $hashref;
        my %yesNoHash = ("1" => "Y", "2" => "N"); my $digestPass; my $md5; 
        %params = ("width" => "300", "align" => "left", "msg" => "...Edit User Page...", "class" => "headerTitleLeft");
        $htmlPage->Header(\%params);
        $htmlPage->ClearAll();
        $htmlPage->TheBR();
	if($userName and $password and $commonName and $qosUpload ne "---" and $qosDownload ne "---" and $buildGraph ne "---" and $activeUser ne "---")
	{
		$md5 = Digest::MD5->new;
		$md5->add("$userName $password");
		$digestPass = $md5->hexdigest;
		$query = "select min,max from qos_limits where id='$qosDownload'";
                $mysqlConn->SetMakeQuery($query);
                $mysqlHash = $mysqlConn->GetHashrow();
                $mysqlConn->EndQuery();
                $downMin = $mysqlHash->{min};
                $downMax = $mysqlHash->{max};
                if(!$downMax) {$downMax = "NULL"; $downMin = "NULL";}
                else {$downMax = "'$downMax'"; $downMin = "'$downMin'";}
                $query = "select min,max from qos_limits where id='$qosUpload'";
                $mysqlConn->SetMakeQuery($query);
                $mysqlHash = $mysqlConn->GetHashrow();
                $mysqlConn->EndQuery();
                $upMax = $mysqlHash->{max};
                $upMin = $mysqlHash->{min};
                if(!$upMin) {$upMin = "NULL"; $upMax = "NULL";}
                else {$upMin = "'$upMin'"; $upMax = "'$upMax'";}
		$query = "update users set username='$userName',password='$digestPass',common_name='$commonName',active='$yesNoHash{$activeUser}',down_min=$downMin,down_max=$downMax,upload_max=$upMax,upload_min=$upMin,graph_active='$yesNoHash{$buildGraph}' where id='$curentUserId'";
		$mysqlConn->SetMakeQuery($query);
		$mysqlConn->EndQuery();			
		ShowUsers();	
		$htmlPage->TheBR();
		%params = ("width" => "400", "align" => "left", "msg" => "...User $userName has been changed...", "class" => "headerTitleLeft");
		$htmlPage->Header(\%params);
		$htmlPage->TheBR();
		$error = CreateUserCertificate($commonName);
	}
	else
	{
        	%params = ("width" => "900", "align" => "center", "cellpadding" => "1", "cellspacing" => "1");
	        $htmlPage->StartTable(\%params);
        	ShowUsersStartHeader();
	        ShowCurrentUser($curentUserId);
        	$htmlPage->EndTable();
	        $htmlPage->TheBR();
                %params = ("method" => "post", "name" => "userEditVerify");
                $htmlPage->StartForm(\%params);
                %params = ("width" => "300", "align" => "left", "cellpadding" => "1", "cellspacing" => "1");
                $htmlPage->StartTable(\%params);
                $style = "teste";
                if(!$userName) {$style = "testeRed";}
                EditUsername($userName,$style);
                $style = "teste";
                if(!$password) {$style = "testeRed";}
                EditPassword($password,$style);
                $style = "teste";
                if(!$commonName) {$style = "testeRed";}
                EditCommonName($commonName, $style);
                $style = "headerLeft";
                if($qosUpload eq "---") {$style = "normalRed";}
                EditQosUpload($qosUpload,$style);
                $style = "headerLeft";
                if($qosDownload eq "---") {$style = "normalRed";}
                EditQosDownload($qosDownload,$style);
                $style = "headerLeft";
                if(!$buildGraph or $buildGraph eq "---") {$style = "normalRed";}
                EditBuildGraph($buildGraph,$style);
		$style = "headerLeft";
                if(!$activeUser or $activeUser eq "---") {$style = "normalRed";}
                EditActiveUser($activeUser,$style);
                AddButton();
                $htmlPage->EndTable();
                %params = ("name" => "action", "value" => "editUserSave");
                $htmlPage->HiddenVar(\%params);
		%params = ("name" => "curentUserId", "value" => "$curentUserId");
		$htmlPage->HiddenVar(\%params);
                $htmlPage->EndForm();	
	}
}
elsif($action eq "deleteUser")
{
	my $curentUserId = $postVars->GetVarSingle("curentUserId");
	%params = ("width" => "300", "align" => "left", "msg" => "...Delete User Page...", "class" => "headerTitleLeft");
	$htmlPage->Header(\%params);
	$htmlPage->ClearAll();
	$htmlPage->TheBR();
	%params = ("width" => "900", "align" => "center", "cellpadding" => "1", "cellspacing" => "1");
	$htmlPage->StartTable(\%params);
	ShowUsersStartHeader();
	ShowCurrentUser($curentUserId,2);	
	%params = ("method" => "post", "target" => "down", "name" => "deleteUserForever");
	$htmlPage->StartForm(\%params);
	$htmlPage->StartRow();
		%params = ("width" => "900", "classTd" => "normal", "classButton" => "buttonInput100", "colspan" => "10", "msg" => "...Delete User...");
		$htmlPage->CellButton(\%params);
	$htmlPage->EndRow();
	%params = ("name" => "action", "value" => "deleteUserForever");
        $htmlPage->HiddenVar(\%params);
	%params = ("name" => "curentUserId", "value" => "$curentUserId");
	$htmlPage->HiddenVar(\%params);
	$htmlPage->EndForm();
	$htmlPage->EndTable();
	$htmlPage->TheBR();

}
if($action eq "deleteUserForever")
{
	my $curentUserId = $postVars->GetVarSingle("curentUserId");
	my $hashrow; my $username; my $commonName; my $hashrow; my $query;
	$query = "select username,common_name from users where id='$curentUserId'";
	$mysqlConn->SetMakeQuery($query);
	$hashrow = $mysqlConn->GetHashrow();
	$mysqlConn->EndQuery(); 
	$username = $hashrow->{username};
	$commonName = $hashrow->{common_name};
	$query = "delete from connextions where username='$username'";
	$mysqlConn->SetMakeQuery($query);
	$mysqlConn->EndQuery();
	$query = "delete from monitor_bandwidth where user_id='$curentUserId'";
	$mysqlConn->SetMakeQuery($query);
	$mysqlConn->EndQuery();
	$query = "delete from users where id='$curentUserId'";
	$mysqlConn->SetMakeQuery($query);
	$mysqlConn->EndQuery();
	%params = ("width" => "300", "align" => "left", "msg" => "...Users Page. Add. Delete. Modify...", "class" => "headerTitleLeft");
	$htmlPage->Header(\%params);
	$htmlPage->ClearAll();
	$htmlPage->TheBR();
	ShowUsers();
	$htmlPage->TheBR();
	%params = ("width" => "300", "align" => "left", "msg" => "...User [$username] deleted...", "class" => "headerTitleLeft");
	$htmlPage->Header(\%params);
	$htmlPage->ClearAll();
	DeleteUserCertificate($commonName);
}
$mysqlConn->StopConnection();
$htmlPage->EndPage();
###############################################################################
sub SetPassword
{
	my $password = shift;
	my $command = "passwd";
}

sub ShowUsers
{
	my %params = (); my $query; my $mysqlHash; 
	my $userName; my $userId;
	%params = ("width" => "950", "align" => "center", "cellpadding" => "1", "cellspacing" => "1");
        $htmlPage->StartTable(\%params);
	ShowUsersStartHeader();
	$query = "select id from users";
	$mysqlConn->SetMakeQuery($query);
	while($mysqlHash = $mysqlConn->GetHashrow())
	{
		$userId = $mysqlHash->{id};
		ShowCurrentUser($userId);
	}	
	$mysqlConn->EndQuery();
        $htmlPage->StartRow();
                %params = ("name" => "addNewUser", "method" => "post");
                $htmlPage->StartForm(\%params);
                %params = ("width" => "50", "classTd" => "headerLeft", "classButton" => "buttonInput100", "msg" => "Add New User", "colspan" => "
10");
                $htmlPage->CellButton(\%params);
                %params = ("name" => "action", "value" => "addNewUser");
                $htmlPage->HiddenVar(\%params);
                $htmlPage->EndForm();
        $htmlPage->EndRow();
	$htmlPage->EndTable();
}


sub ShowCurrentUser
{
	my $userId = shift;
	my $showActions = shift; ## if showActions=1 then buttons Del and Edit will be visible, if showActions=2 buttons will not be visible
	my %params = (); my $query; my $mysqlHash; my $userName; my $msg;
	if(!$showActions) {$showActions = 1;}
	$query = "select * from users where id='$userId'";
	$mysqlConn->SetMakeQuerySecondary($query);
	$mysqlHash = $mysqlConn->GetHashrowSecondary();
	$mysqlConn->EndQuerySecondary();
	$userName = $mysqlHash->{username};
	$htmlPage->StartRow();
        	%params = ("width" => "100", "class" => "headerLeft", "msg" => "$userName");
                $htmlPage->Cell(\%params);
                $params{msg} = $mysqlHash->{common_name};
		$params{width} = 150;
                $htmlPage->Cell(\%params);
                $params{msg} = $mysqlHash->{upload_min}."->".$mysqlHash->{upload_max};
                $htmlPage->Cell(\%params);
                $params{msg} = $mysqlHash->{down_min}."->".$mysqlHash->{down_max};
                $htmlPage->Cell(\%params);
                $params{msg} = "$mysqlHash->{graph_active}";
                $params{width} = 50;
                $htmlPage->Cell(\%params);
                $params{msg} = "$mysqlHash->{active}";
                $htmlPage->Cell(\%params);
                $query = "select count(*) as count from connextions where username='$userName'";
                $mysqlConn->SetMakeQuerySecondary($query);
                $otherHash = $mysqlConn->GetHashrowSecondary();
                $mysqlConn->EndQuerySecondary();
                $params{width} = 100;
		if($otherHash->{count} > 0) {$params{msg} = "$otherHash->{count}";}
		else {$params{msg} = "Never";}
                $htmlPage->Cell(\%params);
                $query = "select time_start,time_stop from connextions where username='$userName' order by time_start desc limit 1";
                $mysqlConn->SetMakeQuerySecondary($query);
                $otherHash = $mysqlConn->GetHashrowSecondary();
                $mysqlConn->EndQuerySecondary();
		if($otherHash->{time_start}){$params{msg} = "$otherHash->{time_start}";}
		else {$params{msg} = "Never";}
                $params{width} = 200;
                $htmlPage->Cell(\%params);
		$msg = "....";
		if($showActions == 1)
		{
			%params = ("method" => "post", "target" => "down", "name" => "editUser");
			$htmlPage->StartForm(\%params);
			%params = ("name" => "action", "value" => "editUser");
			$htmlPage->HiddenVar(\%params);
			%params = ("name" => "curentUserId", "value" => "$userId");
			$htmlPage->HiddenVar(\%params);
			$msg = "Edit";
		}
                %params = ("width" => "50", "classTd" => "headerLeft", "classButton" => "buttonInput100", "msg" => "$msg");
                $htmlPage->CellButton(\%params);
		$msg = "....";
		if($showActions == 1)
		{
			$htmlPage->EndForm();
			%params = ("method" => "post", "target" => "down", "name" => "deleteUser");
			$htmlPage->StartForm(\%params);
			%params = ("name" => "action", "value" => "deleteUser");
			$htmlPage->HiddenVar(\%params);
			%params = ("name" => "curentUserId", "value" => "$userId");
			$htmlPage->HiddenVar(\%params);
			$msg = "Del";
		}
                %params = ("width" => "50", "classTd" => "headerLeft", "classButton" => "buttonInput100", "msg" => "$msg");
                $htmlPage->CellButton(\%params);
		if($showActions == 1) {$htmlPage->EndForm();}
	$htmlPage->EndRow();
}

sub ShowUsersStartHeader
{
	my %params = ();
        $htmlPage->StartRow();
                %params = ("width" => "100", "class" => "headerTable", "msg" => "UserName");
                $htmlPage->Cell(\%params);
                $params{msg} = "Common Name";
		$params{width} = "150";
                $htmlPage->Cell(\%params);
                $params{msg} = "QOS-Upload";
                $htmlPage->Cell(\%params);
                $params{msg} = "QOS-Download";
                $htmlPage->Cell(\%params);
                $params{msg} = "Graph";
                $params{width} = 50;
                $htmlPage->Cell(\%params);
                $params{msg} = "Active";
                $htmlPage->Cell(\%params);
                $params{width} = 100;
                $params{msg} = "LoginCount";
                $htmlPage->Cell(\%params);
                $params{msg} = "LastLogin";
                $params{width} = 200;
                $htmlPage->Cell(\%params);
                $params{width} = 50;
                $params{msg} = "Act1";
                $htmlPage->Cell(\%params);
                $params{msg} = "Act2";
                $htmlPage->Cell(\%params);
	$htmlPage->EndRow();	
}

sub EditUsername
{
	my $userName = shift;
	my $style = shift;
	my %params; my %paramsInput;
       	$htmlPage->StartRow();
                %params = ("width" => "100", "class" => "headerLeft", "msg" => "Username");
                $htmlPage->Cell(\%params);
                %paramsInput = ("width" => "200", "classTd" => "headerLeft", "classInput" => "$style", "name" => "userName", "value" => "$userName");
                $htmlPage->CellInput(\%paramsInput);
        $htmlPage->EndRow();	
}

sub EditPassword
{
	my $password = shift;
	my $style = shift;
	my %params; my %paramsInput;
        $htmlPage->StartRow();
                %params = ("width" => "100", "class" => "headerLeft", "msg" => "Password");
                $htmlPage->Cell(\%params);
                %paramsInput = ("width" => "200", "classTd" => "headerLeft", "classInput" => "$style", "name" => "password", "value" => "", "type" => "password");
		$htmlPage->CellInput(\%paramsInput);
        $htmlPage->EndRow();
}

sub EditCommonName
{
	my $commonName = shift;
	my $style = shift;
	my %params; my %paramsInput;
	$htmlPage->StartRow();
		%params = ("width" => "100", "class" => "headerLeft", "msg" => "Common Name");
		$htmlPage->Cell(\%params);
		%paramsInput = ("width" => "200", "classTd" => "headerLeft", "classInput" => "$style", "name" => "commonName", "value" => "$commonName");
		$htmlPage->CellInput(\%paramsInput);
	$htmlPage->EndRow();
}

sub EditQosUpload
{
	my $qosUpload = shift;
	my $style = shift;
	my %params; my %paramsSelect; my $query; my $mysqlHash; my %selectValues;
	$htmlPage->StartRow();
                %params = ("width" => "100", "class" => "headerLeft", "msg" => "QOS-Upload");
		$htmlPage->Cell(\%params);
                %paramsSelect = ("width" => "200", "classTd" => "headerLeft", "classSelect" => "$style", "name" => "qosUpload", "selId" => "$qosUpload");
                $query = "select id,name from qos_limits";
                $mysqlConn->SetMakeQuery($query);
                while($mysqlHash = $mysqlConn->GetHashrow())
                {
                        $selectValues{$mysqlHash->{id}} = $mysqlHash->{name};
                }
                $mysqlConn->EndQuery();
                $htmlPage->CellSelect(\%paramsSelect,\%selectValues);
	$htmlPage->EndRow();
}

sub EditQosDownload
{
	my $qosDownload = shift;
	my $style = shift;
	my %params; my %paramsSelect; my $query; my $mysqlHash; my %selectValues;
	$htmlPage->StartRow();
		%params = ("width" => "100", "class" => "headerLeft", "msg" => "QOS-Download");
		$htmlPage->Cell(\%params);
		%paramsSelect = ("width" => "200", "classTd" => "headerLeft", "classSelect" => "$style", "name" => "qosDownload", "selId" => "$qosDownload");
		$query = "select id,name from qos_limits";
		$mysqlConn->SetMakeQuery($query);
		while($mysqlHash = $mysqlConn->GetHashrow())
		{
			$selectValues{$mysqlHash->{id}} = $mysqlHash->{name};
		}
		$mysqlConn->EndQuery();
		$htmlPage->CellSelect(\%paramsSelect,\%selectValues);
	$htmlPage->EndRow();
}

sub EditBuildGraph
{
	my $buildGraph = shift;
	my $style = shift;
	my %params; my %paramsSelect; my %selectValues = ("1" => "Yes", "2" => "No");
	$htmlPage->StartRow();
		%params = ("width" => "100", "class" => "headerLeft", "msg" => "Build Graph");
		$htmlPage->Cell(\%params);
		%paramsSelect = ("width" => "200", "classTd" => "headerLeft", "classSelect" => "$style", "name" => "buildGraph", "selId" => "$buildGraph");
		$htmlPage->CellSelect(\%paramsSelect,\%selectValues);
	$htmlPage->EndRow();
}

sub EditActiveUser
{
	my $activeUser = shift;
	my $style = shift;
	my %params; my %paramsSelect; my %selectValues = ("1" => "Yes", "2" => "No");
	$htmlPage->StartRow();
		%params = ("width" => "100", "class" => "headerLeft", "msg" => "Active User");
		$htmlPage->Cell(\%params);
		%paramsSelect = ("width" => "200", "classTd" => "headerLeft", "classSelect" => "$style", "name" => "activeUser", "selId" => "$activeUser");
		$htmlPage->CellSelect(\%paramsSelect,\%selectValues);
	$htmlPage->EndRow();
}

sub AddButton
{
	my $msg = shift;
	if(!$msg) {$msg = "Add User";}
	$htmlPage->StartRow();
        	%params = ("width" => "300", "classTd" => "headerLeft", "classButton" => "buttonInput100", "colspan" => "2", "msg" => "$msg");
                $htmlPage->CellButton(\%params);
        $htmlPage->EndRow();
}

sub DeleteUserCertificate
{
	my $commonName = shift;
	my $temp; my @files; my %params;
	my $command; my $commandOutput; my $sem = 1; ## files do not exists
	if(!$commonName)
	{
		%params = ("width" => "500", "align" => "left", "msg" => "...A nasty error ocured. No commonName was received...", "class" => "headerTitleLeft");
		$htmlPage->Header(\%params);
		$htmlPage->TheBR();
		return;
	}
	opendir(IMD,$opvKeyPath);
	@files = readdir(IMD);
	foreach $temp (@files) {if($temp =~ $commonName){$sem++;}}
	closedir(IMD);
	if($sem > 1) ## files do exists and will try to delete them
	{
		$command = "rm -f $opvKeyPath/$commonName".".*";
		`$command`;
		$sem = 1;
		opendir(IMD,$opvKeyPath);
		@files = readdir(IMD);
		foreach $temp (@files) {if($temp =~ $commonName){$sem++;}}
		closedir(IMD);
		if($sem == 1)
		{
			%params = ("width" => "500", "align" => "left", "msg" => "...Certificate was deleted...", "class" => "headerTitleLeft");
			$htmlPage->Header(\%params);
			$htmlPage->TheBR();
		}
		else
		{
			%params = ("width" => "500", "align" => "left", "msg" => "...A problem ocurred in deleteing the certificate...", "class" => "headerTitleLeft");
			$htmlPage->Header(\%params);
			$htmlPage->TheBR();
			return;
		}
	}
}

sub CreateUserCertificate
{
	my $commonName = shift;
	my $temp; my @files; my %params; my $sem = 1; ## files do not exists
	my $command; my $commandOutput;
	if(!$commonName) 
	{
		%params = ("width" => "500", "align" => "left", "msg" => "...A nasty error ocured. No commonName was received...", "class" => "headerTitleLeft");
		$htmlPage->Header(\%params);
		$htmlPage->TheBR();
		return;
	}
        opendir(IMD,$opvKeyPath);
        @files = readdir(IMD);
        foreach $temp (@files)
        {
	        if($temp =~ $commonName)
                {
                	%params = ("width" => "500", "align" => "left", "msg" => "...A certificate with that common_name already exists. Deleting...", "class" => "headerTitleLeft");
                        $htmlPage->Header(\%params);
                        $htmlPage->TheBR();
                        $sem = 2;
                        last;
                }
        }        
        if($sem == 2)
        {        
                $command = "rm -f $commonName".".*";         
               `$command`;                
	}        
        closedir(IMD);
        $command = $opvBinPath."createUserCertificate.pl $commonName";
        $commandOutput = `$command`;
        opendir(IMD,$opvKeyPath);
        @files = readdir(IMD);
        $sem = 1; ##to be ok sem = 4 => we need 3 files ...
        foreach $temp (@files) {if($temp =~ $commonName) {$sem++;}}
        if($sem == 4)
        {
	        %params = ("width" => "400", "align" => "left", "msg" => "...Create certificate. Success...", "class" => "headerTitleLeft");
                $htmlPage->Header(\%params);
                $htmlPage->TheBR();
        }
        else
        {
        	%params = ("width" => "400", "align" => "left", "msg" => "...Something bad happend in creating the certificates...", "class" => "headerTitleLeft");
                $htmlPage->Header(\%params);
                $htmlPage->TheBR();
        }
}
