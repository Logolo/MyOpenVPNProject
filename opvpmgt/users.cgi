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
	$htmlPage->Header({"width" => "300", "align" => "left", "msg" => "Users Page. Add. Delete. Modify.", "class" => "headerTitleLeft"});
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
        $htmlPage->Header({"width" => "300", "align" => "left", "msg" => "...Add New User Page...", "class" => "headerTitleLeft"});
        $htmlPage->ClearAll();
        $htmlPage->TheBR();
	$htmlPage->StartForm({"method" => "post", "name" => "userAddVerify"});
        $htmlPage->StartTable({"width" => "300", "align" => "left"});
	EditUsername($userName, "teste");
	EditPassword($password, "teste");
	EditCommonName($commonName, "teste");
	EditQosUpload($qosUpload, "normal");
	EditQosDownload($qosDownload, "normal");
	EditBuildGraph($buildGraph, "normal");
	EditActiveUser($activeUser, "normal");
	AddButton();
	$htmlPage->EndTable();
	$htmlPage->HiddenVar({"name" => "action", "value" => "addNewUserStepOne"});
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
        	$htmlPage->Header({"width" => "300", "align" => "left", "msg" => "Users Page. Add. Delete. Modify.", "class" => "headerTitleLeft"});
	        $htmlPage->ClearAll();
        	$htmlPage->TheBR();
	        ShowUsers();
        	$htmlPage->TheBR();
		CreateUserCertificate($commonName);
	}
	else
	{
		$htmlPage->Header({"width" => "300", "align" => "left", "msg" => "...Add New User Page...", "class" => "headerTitleLeft"});
		$htmlPage->ClearAll();
		$htmlPage->TheBR();
	        $htmlPage->StartForm({"method" => "post", "name" => "userAddVerify"});
		$htmlPage->StartTable({"width" => "300", "align" => "left"});
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
		$style = "normal";
		if($qosDownload eq "---") {$style = "normalRed";}
		EditQosDownload($qosDownload,$style);
		$style = "normal";
		if(!$buildGraph or $buildGraph eq "---") {$style = "normalRed";} 
		EditBuildGraph($buildGraph,$style);
		$style = "normal";
		if(!$activeUser or $activeUser eq "---") {$style = "normalRed";}
		EditActiveUser($activeUser,$style);
		AddButton();
		$htmlPage->EndTable();
		$htmlPage->HiddenVar({"name" => "action", "value" => "addNewUserStepOne"});
		$htmlPage->EndForm();
		if($duplicat == 2)
		{
			$htmlPage->ClearAll();
			$htmlPage->TheBR();
			$htmlPage->Header({"width" => "300", "align" => "left", "msg" => "...Username is already used...", "class" => "headerTitleLeft"});
			$htmlPage->TheBR();
		}
	}
}
elsif($action eq "editUser")
{
	my $curentUserId = $postVars->GetVarSingle("curentUserId");
	my $query; my $hashref; my $sechashref; my %yesnoHash = ("Y" => "1", "N" => "2");
        $htmlPage->Header({"width" => "300", "align" => "left", "msg" => "...Edit User Page...", "class" => "headerTitleLeft"});
        $htmlPage->ClearAll();
        $htmlPage->TheBR();
	$htmlPage->StartTable({"width" => "950", "align" => "center"});
	ShowUsersStartHeader();
	ShowCurrentUser($curentUserId);
	$htmlPage->EndTable();
	$htmlPage->TheBR();
	$query = "select * from users where id='$curentUserId'";
	$mysqlConn->SetMakeQuery($query);
	$hashref = $mysqlConn->GetHashrow();
	$mysqlConn->EndQuery();
        $htmlPage->StartTable({"width" => "300", "align" => "left"});
	$htmlPage->StartForm({"name" => "editUserSave", "method" => "post"});
        EditUsername($hashref->{username}, "teste");
        EditPassword("anyText", "teste");
        EditCommonName($hashref->{common_name}, "teste");
	$query = "select id from qos_limits where min='$hashref->{upload_min}' and max='$hashref->{upload_max}'";
	$mysqlConn->SetMakeQuery($query);
	$sechashref = $mysqlConn->GetHashrow();
	$mysqlConn->EndQuery();
        EditQosUpload($sechashref->{id}, "normal");
	$query = "select id from qos_limits where min='$hashref->{down_min}' and max='$hashref->{down_max}'";
	$mysqlConn->SetMakeQuery($query);
	$sechashref = $mysqlConn->GetHashrow();
	$mysqlConn->EndQuery();
        EditQosDownload($sechashref->{id}, "normal");
        EditBuildGraph($yesnoHash{$hashref->{graph_active}}, "normal");
        EditActiveUser($yesnoHash{$hashref->{active}}, "normal");
        AddButton("Modify User");
	$htmlPage->HiddenVar({"name" => "action", "value" => "editUserSave"});
	$htmlPage->HiddenVar({"name" => "curentUserId", "value" => "$curentUserId"});
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
        $htmlPage->Header({"width" => "300", "align" => "left", "msg" => "...Edit User Page...", "class" => "headerTitleLeft"});
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
		$htmlPage->Header({"width" => "400", "align" => "left", "msg" => "...User $userName has been changed...", "class" => "headerTitleLeft"});
		$htmlPage->TheBR();
		$error = CreateUserCertificate($commonName);
	}
	else
	{
	        $htmlPage->StartTable({"width" => "950", "align" => "center"});
        	ShowUsersStartHeader();
	        ShowCurrentUser($curentUserId);
        	$htmlPage->EndTable();
	        $htmlPage->TheBR();
                $htmlPage->StartForm({"method" => "post", "name" => "userEditVerify"});
                $htmlPage->StartTable({"width" => "300", "align" => "left"});
                $style = "teste";
                if(!$userName) {$style = "testeRed";}
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
                $style = "normal";
                if($qosDownload eq "---") {$style = "normalRed";}
                EditQosDownload($qosDownload,$style);
                $style = "normal";
                if(!$buildGraph or $buildGraph eq "---") {$style = "normalRed";}
                EditBuildGraph($buildGraph,$style);
		$style = "normal";
                if(!$activeUser or $activeUser eq "---") {$style = "normalRed";}
                EditActiveUser($activeUser,$style);
                AddButton();
                $htmlPage->EndTable();
                $htmlPage->HiddenVar({"name" => "action", "value" => "editUserSave"});
		$htmlPage->HiddenVar({"name" => "curentUserId", "value" => "$curentUserId"});
                $htmlPage->EndForm();	
	}
}
elsif($action eq "deleteUser")
{
	my $curentUserId = $postVars->GetVarSingle("curentUserId");
	$htmlPage->Header({"width" => "300", "align" => "left", "msg" => "...Delete User Page...", "class" => "headerTitleLeft"});
	$htmlPage->ClearAll();
	$htmlPage->TheBR();
	$htmlPage->StartTable({"width" => "950", "align" => "center"});
	ShowUsersStartHeader();
	ShowCurrentUser($curentUserId,2);	
	$htmlPage->StartForm({"method" => "post", "target" => "down", "name" => "deleteUserForever"});
	$htmlPage->StartRow();
		$htmlPage->CellButton({"width" => "950", "classTd" => "normal", "classButton" => "buttonInput100", "colspan" => "10", "msg" => "...Delete User..."});
	$htmlPage->EndRow();
        $htmlPage->HiddenVar({"name" => "action", "value" => "deleteUserForever"});
	$htmlPage->HiddenVar({"name" => "curentUserId", "value" => "$curentUserId"});
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
	$query = "delete from monitor_users where user_id='$curentUserId'";
	$mysqlConn->SetMakeQuery($query);
	$mysqlConn->EndQuery();
	$query = "delete from users where id='$curentUserId'";
	$mysqlConn->SetMakeQuery($query);
	$mysqlConn->EndQuery();
	$htmlPage->Header({"width" => "300", "align" => "left", "msg" => "...Users Page. Add. Delete. Modify...", "class" => "headerTitleLeft"});
	$htmlPage->ClearAll();
	$htmlPage->TheBR();
	ShowUsers();
	$htmlPage->TheBR();
	$htmlPage->Header({"width" => "300", "align" => "left", "msg" => "...User [$username] deleted...", "class" => "headerTitleLeft"});
	$htmlPage->ClearAll();
	DeleteUserCertificate($commonName);
}
elsif($action eq "showHistoryUser")
{
	my $curentUserId = $postVars->GetVarSingle("curentUserId");
	my $count = 0; my $mysqlHash; my $userName;
	$htmlPage->Header({"width" => "300", "align" => "left", "msg" => "...Show Connection History...", "class" => "headerTitleLeft"});
	$htmlPage->ClearAll();
	$htmlPage->TheBR();
	$htmlPage->StartTable({"width" => "950", "align" => "center"});
	ShowUsersStartHeader();
	ShowCurrentUser($curentUserId);
	$htmlPage->EndTable();
	$htmlPage->ClearAll();
	$htmlPage->TheHR();
	$htmlPage->StartTable({"width" => "910", "align" => "center"});
	$htmlPage->StartRow();
		$htmlPage->Cell({"width" => "10", "class" => "headerTable", "msg" => "Nr."});
		$htmlPage->Cell({"width" => "200", "class" => "headerTable", "msg" => "Start Date"});
		$htmlPage->Cell({"width" => "200", "class" => "headerTable", "msg" => "End Date"});
		$htmlPage->Cell({"width" => "100", "class" => "headerTable", "msg" => "Upload(B)"});
		$htmlPage->Cell({"width" => "100", "class" => "headerTable", "msg" => "Download(B)"});
		$htmlPage->Cell({"width" => "150", "class" => "headerTable", "msg" => "Remote IP"});
		$htmlPage->Cell({"width" => "150", "class" => "headerTable", "msg" => "Remote Local IP"});
	$htmlPage->EndRow();
	$query = "select username from users where id='$curentUserId'";
	$mysqlConn->SetMakeQuery($query);
	$mysqlHash = $mysqlConn->GetHashrow();
	$mysqlConn->EndQuery();
	$userName = $mysqlHash->{username};
	$query = "select remote_ip, remote_private_ip, bytes_sent, bytes_received, time_start, time_stop, time_duration from connextions where username='$userName' order by time_start";
	$mysqlConn->SetMakeQuery($query);
	while($mysqlHash = $mysqlConn->GetHashrow())
	{
		$count++;
		$htmlPage->StartRow();
			$htmlPage->Cell({"width"=>"10","class"=>"headerLeft","msg"=>"$count"});
			$htmlPage->Cell({"width"=>"200","class"=>"headerLeft","msg"=>$mysqlHash->{time_start}});
			$htmlPage->Cell({"width"=>"200","class"=>"headerLeft","msg"=>$mysqlHash->{time_stop}});
			$htmlPage->Cell({"width"=>"100","class"=>"headerLeft","msg"=>$mysqlHash->{bytes_received}});
			$htmlPage->Cell({"width"=>"100","class"=>"headerLeft","msg"=>$mysqlHash->{bytes_sent}});
			$htmlPage->Cell({"width"=>"150","class"=>"headerLeft","msg"=>$mysqlHash->{remote_private_ip}});
			$htmlPage->Cell({"width"=>"150","class"=>"headerLeft","msg"=>$mysqlHash->{remote_ip}});
		$htmlPage->EndRow();
	}
	$mysqlConn->EndQuery();
	$htmlPage->EndTable();
}
$mysqlConn->StopConnection();
$htmlPage->EndPage();
###############################################################################

sub ShowUsers
{
	my %params = (); my $query; my $mysqlHash; 
	my $userName; my $userId;
        $htmlPage->StartTable({"width" => "950", "align" => "center"});
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
                $htmlPage->StartForm({"name" => "addNewUser", "method" => "post"});
                %params = ("width" => "50", "classTd" => "headerLeft", "classButton" => "buttonInput100", "msg" => "Add New User", "colspan" => "
10");
                $htmlPage->CellButton({"width" => "50", "classTd" => "headerLeft", "classButton" => "buttonInput100", "msg" => "Add New User", "colspan" => "10"});
                $htmlPage->HiddenVar({"name" => "action", "value" => "addNewUser"});
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
                $htmlPage->Cell({"width" => "100", "class" => "headerLeft", "msg" => "$userName"});
                $htmlPage->Cell({"width" => "150", "class" => "headerLeft", "msg" => $mysqlHash->{common_name}});
                $msg = $mysqlHash->{upload_min}."->".$mysqlHash->{upload_max};
                $htmlPage->Cell({"width" => "150", "class" => "headerLeft", "msg" => "$msg"});
                $msg = $mysqlHash->{down_min}."->".$mysqlHash->{down_max};
                $htmlPage->Cell({"width" => "150", "class" => "headerLeft", "msg" => "$msg"});
                $htmlPage->Cell({"width" => "50", "class" => "headerLeft", "msg" => $mysqlHash->{graph_active}});
                $htmlPage->Cell({"width" => "50", "class" => "headerLeft", "msg" => $mysqlHash->{active}});
                $query = "select count(*) as count from connextions where username='$userName'";
                $mysqlConn->SetMakeQuerySecondary($query);
                $otherHash = $mysqlConn->GetHashrowSecondary();
                $mysqlConn->EndQuerySecondary();
		if($otherHash->{count} > 0) {$msg = "$otherHash->{count}";}
		else {$msg = "Never";}
		$htmlPage->StartForm({"name" => "showHistory", "method" => "post"});
		$htmlPage->CellButton({"width" => "100", "classTd" => "headerLeft", "classButton" => "buttonInput100Doi", "msg" => $msg});
		$htmlPage->HiddenVar({"name" => "action", "value" => "showHistoryUser"});	
		$htmlPage->HiddenVar({"name" => "curentUserId", "value" => "$userId"});
		$htmlPage->EndForm();
                $query = "select time_start,time_stop from connextions where username='$userName' order by time_start desc limit 1";
                $mysqlConn->SetMakeQuerySecondary($query);
                $otherHash = $mysqlConn->GetHashrowSecondary();
                $mysqlConn->EndQuerySecondary();
		if($otherHash->{time_start}){$msg = "$otherHash->{time_start}";}
		else {$msg = "Never";}
                $params{width} = 200;
                $htmlPage->Cell({"width" => "200", "class" => "headerLeft", "msg" => "$msg"});
		$msg = "....";
		if($showActions == 1)
		{
			$htmlPage->StartForm({"method" => "post", "target" => "down", "name" => "editUser"});
			$htmlPage->HiddenVar({"name" => "action", "value" => "editUser"});
			$htmlPage->HiddenVar({"name" => "curentUserId", "value" => "$userId"});
			$msg = "Edit";
		}
                $htmlPage->CellButton({"width" => "50", "classTd" => "headerLeft", "classButton" => "buttonInput100", "msg" => "$msg"});
		$msg = "....";
		if($showActions == 1)
		{
			$htmlPage->EndForm();
			$htmlPage->StartForm({"method" => "post", "target" => "down", "name" => "deleteUser"});
			$htmlPage->HiddenVar({"name" => "action", "value" => "deleteUser"});
			$htmlPage->HiddenVar({"name" => "curentUserId", "value" => "$userId"});
			$msg = "Del";
		}
                $htmlPage->CellButton({"width" => "50", "classTd" => "headerLeft", "classButton" => "buttonInput100", "msg" => "$msg"});
		if($showActions == 1) {$htmlPage->EndForm();}
	$htmlPage->EndRow();
}

sub ShowUsersStartHeader
{
	my %params = ();
        $htmlPage->StartRow();
                $htmlPage->Cell({"width" => "100", "class" => "headerTable", "msg" => "UserName"});
                $htmlPage->Cell({"width" => "150", "class" => "headerTable", "msg" => "Common Name"});
                $htmlPage->Cell({"width" => "150", "class" => "headerTable", "msg" => "QOS-Upload"});
                $htmlPage->Cell({"width" => "150", "class" => "headerTable", "msg" => "QOS-Download"});
                $htmlPage->Cell({"width" => "50", "class" => "headerTable", "msg" => "Graph"});
                $htmlPage->Cell({"width" => "50", "class" => "headerTable", "msg" => "Active"});
                $htmlPage->Cell({"width" => "100", "class" => "headerTable", "msg" => "LoginCount"});
                $htmlPage->Cell({"width" => "200", "class" => "headerTable", "msg" => "LastLogin"});
                $htmlPage->Cell({"width" => "50", "class" => "headerTable", "msg" => "Act1"});
                $htmlPage->Cell({"width" => "50", "class" => "headerTable", "msg" => "Act2"});
	$htmlPage->EndRow();	
}

sub EditUsername
{
	my $userName = shift;
	my $style = shift;
	my %params; my %paramsInput;
       	$htmlPage->StartRow();
                $htmlPage->Cell({"width" => "100", "class" => "headerLeft", "msg" => "Username"});
                $htmlPage->CellInput({"width" => "200", "classTd" => "headerLeft", "classInput" => "$style", "name" => "userName", "value" => "$userName"});
        $htmlPage->EndRow();	
}

sub EditPassword
{
	my $password = shift;
	my $style = shift;
	my %params; my %paramsInput;
        $htmlPage->StartRow();
                $htmlPage->Cell({"width" => "100", "class" => "headerLeft", "msg" => "Password"});
		$htmlPage->CellInput({"width" => "200", "classTd" => "headerLeft", "classInput" => "$style", "name" => "password", "value" => "", "type" => "password"});
        $htmlPage->EndRow();
}

sub EditCommonName
{
	my $commonName = shift;
	my $style = shift;
	my %params; my %paramsInput;
	$htmlPage->StartRow();
		$htmlPage->Cell({"width" => "100", "class" => "headerLeft", "msg" => "Common Name"});
		$htmlPage->CellInput({"width" => "200", "classTd" => "headerLeft", "classInput" => "$style", "name" => "commonName", "value" => "$commonName"});
	$htmlPage->EndRow();
}

sub EditQosUpload
{
	my $qosUpload = shift;
	my $style = shift;
	my %params; my %paramsSelect; my $query; my $mysqlHash; my %selectValues;
	$htmlPage->StartRow();
		$htmlPage->Cell({"width" => "100", "class" => "headerLeft", "msg" => "QOS-Upload"});
                $query = "select id,name from qos_limits";
                $mysqlConn->SetMakeQuery($query);
                while($mysqlHash = $mysqlConn->GetHashrow())
                {
                        $selectValues{$mysqlHash->{id}} = $mysqlHash->{name};
                }
                $mysqlConn->EndQuery();
                $htmlPage->CellSelect({"width" => "200", "classTd" => "headerLeft", "classSelect" => "$style", "name" => "qosUpload", "selId" => "$qosUpload"},\%selectValues);
	$htmlPage->EndRow();
}

sub EditQosDownload
{
	my $qosDownload = shift;
	my $style = shift;
	my %params; my %paramsSelect; my $query; my $mysqlHash; my %selectValues;
	$htmlPage->StartRow();
		$htmlPage->Cell({"width" => "100", "class" => "headerLeft", "msg" => "QOS-Download"});
		$query = "select id,name from qos_limits";
		$mysqlConn->SetMakeQuery($query);
		while($mysqlHash = $mysqlConn->GetHashrow())
		{
			$selectValues{$mysqlHash->{id}} = $mysqlHash->{name};
		}
		$mysqlConn->EndQuery();
		$htmlPage->CellSelect({"width" => "200", "classTd" => "headerLeft", "classSelect" => "$style", "name" => "qosDownload", "selId" => "$qosDownload"},\%selectValues);
	$htmlPage->EndRow();
}

sub EditBuildGraph
{
	my $buildGraph = shift;
	my $style = shift;
	my %params; my %paramsSelect; my %selectValues = ("1" => "Yes", "2" => "No");
	$htmlPage->StartRow();
		$htmlPage->Cell({"width" => "100", "class" => "headerLeft", "msg" => "Build Graph"});
		$htmlPage->CellSelect({"width" => "200", "classTd" => "headerLeft", "classSelect" => "$style", "name" => "buildGraph", "selId" => "$buildGraph"},\%selectValues);
	$htmlPage->EndRow();
}

sub EditActiveUser
{
	my $activeUser = shift;
	my $style = shift;
	my %params; my %paramsSelect; my %selectValues = ("1" => "Yes", "2" => "No");
	$htmlPage->StartRow();
		$htmlPage->Cell({"width" => "100", "class" => "headerLeft", "msg" => "Active User"});
		$htmlPage->CellSelect({"width" => "200", "classTd" => "headerLeft", "classSelect" => "$style", "name" => "activeUser", "selId" => "$activeUser"},\%selectValues);
	$htmlPage->EndRow();
}

sub AddButton
{
	my $msg = shift;
	if(!$msg) {$msg = "Add User";}
	$htmlPage->StartRow();
                $htmlPage->CellButton({"width" => "300", "classTd" => "headerLeft", "classButton" => "buttonInput100", "colspan" => "2", "msg" => "$msg"});
        $htmlPage->EndRow();
}

sub DeleteUserCertificate
{
	my $commonName = shift;
	my $temp; my @files; my %params;
	my $command; my $commandOutput; my $sem = 1; ## files do not exists
	if(!$commonName)
	{
		$htmlPage->Header({"width" => "500", "align" => "left", "msg" => "...A nasty error ocured. No commonName was received...", "class" => "headerTitleLeft"});
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
			$htmlPage->Header({"width" => "500", "align" => "left", "msg" => "...Certificate was deleted...", "class" => "headerTitleLeft"});
			$htmlPage->TheBR();
		}
		else
		{
			$htmlPage->Header({"width" => "500", "align" => "left", "msg" => "...A problem ocurred in deleteing the certificate...", "class" => "headerTitleLeft"});
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
		$htmlPage->Header({"width" => "500", "align" => "left", "msg" => "...A nasty error ocured. No commonName was received...", "class" => "headerTitleLeft"});
		$htmlPage->TheBR();
		return;
	}
        opendir(IMD,$opvKeyPath);
        @files = readdir(IMD);
        foreach $temp (@files)
        {
	        if($temp =~ $commonName)
                {
                        $htmlPage->Header({"width" => "500", "align" => "left", "msg" => "...A certificate with that common_name already exists. Deleting...", "class" => "headerTitleLeft"});
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
                $htmlPage->Header({"width" => "400", "align" => "left", "msg" => "...Create certificate. Success...", "class" => "headerTitleLeft"});
                $htmlPage->TheBR();
        }
        else
        {
                $htmlPage->Header({"width" => "400", "align" => "left", "msg" => "...Something bad happend in creating the certificates...", "class" => "headerTitleLeft"});
                $htmlPage->TheBR();
        }
}
