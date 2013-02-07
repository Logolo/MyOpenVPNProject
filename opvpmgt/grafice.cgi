#!/usr/bin/perl

use lib "modules";
use HtmlObject;
use mysqlFunctions;
use PostVars;
use Cwd;


my $htmlPage; my %params = (); my $otherHash; my $action; my $postVars;
my $mysqlConn; my $mysqlError; my $query; my $mysqlHash; my $userName; my $userId;
###############################################################################
$postVars = PostVars->new();
$htmlPage = HtmlObject->new();
$htmlPage->StartPage({"ageTitle" => "OpenVPN Mng", "cssStyle" => "style.css"});
$mysqlConn = MysqlConnection->new();
$mysqlError = $mysqlConn->StartConnection();
if($mysqlError == 10)
{
	$htmlPage->Header({"width" => "400", "class" => "headerTitleLeft", "msg" => "Mysql Error Connextion"});
	exit(0);
}
$htmlPage->Header({"width" => "400", "class" => "headerTitleLeft", "msg" => "Select User and time span to build graph"});
$htmlPage->TheBR();
$action = $postVars->GetVarSingle("action");
if(!$action)
{
	$htmlPage->StartTable({"width" => "250", "align" => "left"});
	StepZero($userNameId);
	$htmlPage->EndTable();
}
elsif($action eq "stepOne")
{
	my $userNameId = $postVars->GetVarSingle("userNameId");
	$htmlPage->StartTable({"width" => "250", "align" => "left"});
	StepZero($userNameId);
	StepOne($userNameId);
	$htmlPage->EndTable();
}
elsif($action eq "stepTwo")
{
	my $userNameId = $postVars->GetVarSingle("userNameId");
	my $dateDayStart = $postVars->GetVarSingle("dateDayStart");
	$htmlPage->StartTable({"width" => "250", "align" => "left"});
	StepZero($userNameId);
	StepOne($userNameId,$dateDayStart);
	StepTwo($userNameId,$dateDayStart);
	$htmlPage->EndTable();
}
elsif($action eq "generateGraph")
{
	my $userNameId = $postVars->GetVarSingle("userNameId");
	my $dateDayStart = $postVars->GetVarSingle("dateDayStart");
	my $dateDayStop = $postVars->GetVarSingle("dateDayStop");
	my $rrdFilePath = "rrdDir/"; 
	my $pngDailyPath = "$rrdFilePath"."$userNameId"."-daily.png";
	my $pngMonthlyPath = "$rrdFilePath"."$userNameId"."-monthly.png";
	my $pngWeeklyPath = "$rrdFilePath"."$userNameId"."-weekly.png";
	my $pngAnnualPath = "$rrdFilePath"."$userNameId"."-annual.png";
	$htmlPage->StartTable({"width" => "250", "align" => "left"});
	StepZero($userNameId);
	StepOne($userNameId,$dateDayStart);
	StepTwo($userNameId,$dateDayStart,$dateDayStop);
	LastStep($userNameId,$dateDayStart,$dateDayStop);
	$htmlPage->EndTable();
	$htmlPage->ClearAll();
	$htmlPage->TheBR();
	$htmlPage->Header({"width" => "400", "class" => "headerTitleLeft", "msg" => "Graphs created succesfully"});
	$htmlPage->TheHR();
	$htmlPage->StartTable({"width" => "250", "align" => "center"});
	$htmlPage->StartRow();
		$htmlPage->CellImage({"width" => "300", "classTd" => "normal", "src" => "$pngDailyPath"});
		$htmlPage->CellImage({"width" => "300", "classTd" => "normal", "src" => "$pngWeeklyPath"});
	$htmlPage->EndRow();
	$htmlPage->StartRow();
		$htmlPage->CellImage({"width" => "300", "classTd" => "normal", "src" => "$pngMonthlyPath"});
		$htmlPage->CellImage({"width" => "300", "classTd" => "normal", "src" => "$pngAnnualPath"});
	$htmlPage->EndRow();
	$htmlPage->EndTable();
}
$mysqlConn->StopConnection();
###############################################################################
sub LastStep
{
	use RRD::Simple;
	use POSIX;
	my ($userNameId,$dateDayStart,$dateDayStop) = @_;
	my $rrdFilePath = "rrdDir/"; my $unixTimeOne; my $unixTimeTwo; my $downRate; my $upRate; my $rrdFileHandler;
	my @dataDayOne; my @dataTimeOne; my $command; 
	my $mysqlHashOne; my $count = 0; my $i; my $query; my %params; my $rrdFileName; 
	my $dateStart; my $dateStop; #actual days ... dateDayStart and dateDayStop are just simple numbers
	if($dateDayStop eq "---" or !$dateDayStop)
	{
		$htmlPage->StartRow();
			$htmlPage->Cell({"width" => "300", "class" => "headerWarning", "msg" => "Incorect Stop Date", "colspan" => "2"});
		$htmlPage->EndRow();
	}
	else
	{
		$command = "rm -f $rrdFilePath"."$userNameId*";
		`$command`;
		$rrdFileName = "$rrdFilePath"."$userNameId.rrd";
		$rrdFileHandler = RRD::Simple->new( file => "$rrdFileName" );
		$rrdFileHandler->create("DOWN_RATE" => "GAUGE", "UP_RATE" => "GAUGE");
		$query = "select date_day from monitor_users where user_id='$userNameId' and id='$dateDayStart'";
		$mysqlConn->SetMakeQuery($query);
		$mysqlHash = $mysqlConn->GetHashrow();
		$dateStart = $mysqlHash->{date_day};
		$mysqlConn->EndQuery();
		$query = "select date_day from monitor_users where user_id='$userNameId' and id='$dateDayStop'";
		$mysqlConn->SetMakeQuery($query);
		$mysqlHash = $mysqlConn->GetHashrow();
		$dateStop = $mysqlHash->{date_day};
		$mysqlConn->EndQuery();
		$query = "select * from monitor_users where user_id='$userNameId' and date_day>='$dateStart' and date_day<='$dateStop' order by date_day,date_time";
		$mysqlConn->SetMakeQuery($query);
		$count = 0; $unixTimeOne = 0;
		while($mysqlHashOne = $mysqlConn->GetHashrow())
		{
			$count++;
			@dataDayOne = split('-', $mysqlHashOne->{date_day});
			@dataTimeOne = split(':', $mysqlHashOne->{date_time});
			$dataDayOne[0] -= 1900;
			$dataDayOne[1] -= 1;
			$unixTimeTwo = mktime($dataTimeOne[2],$dataTimeOne[1],$dataTimeOne[0],$dataDayOne[2],$dataDayOne[1],$dataDayOne[0]);
			if($unixTimeTwo <= $unixTimeOne) {$unixTimeTwo = $unixTimeOne + 1;}
			$rrdFileHandler->update($rrdFileName,$unixTimeTwo,"DOWN_RATE" => $mysqlHashOne->{down_rate}, "UP_RATE" => $mysqlHashOne->{up_rate});
			$unixTimeOne = $unixTimeTwo;
		}
		$mysqlConn->EndQuery();
		$rrdFileHandler->graph("destination" => "$rrdFilePath", "title" => "$userNameId Traffic", "vertical_label" => "TRAFFIC-KILOBITS");
	}	
}

sub StepTwo
{
	my $userNameId = shift;
	my $dateDayStart = shift;
	my $dateDayStop = shift;
	my $realDayStart; 
	my $query; my %params; my $mysqlHash;
	my %params; my $count = 0;
	if($dateDayStart eq "---" or !$dateDayStart)
	{
		$htmlPage->StartRow();
			$htmlPage->Cell({"width" => "300", "class" => "headerWarning", "msg" => "Date Start NOT OK", "colspan" => "2"});
		$htmlPage->EndRow();
	}
	else
	{
		$htmlPage->StartForm({"name" => "lastStep", "method" => "post", "target" => "down"});
		$htmlPage->StartRow();
			$htmlPage->Cell({"width" => "100", "class" => "headerLeft", "msg" => "End Date"});
			$query = "select date_day from monitor_users where user_id='$userNameId' and id='$dateDayStart'";
			$mysqlConn->SetMakeQuery($query);
			$mysqlHash = $mysqlConn->GetHashrow();
			$realDayStart = $mysqlHash->{date_day};
			$mysqlConn->EndQuery();
			$query = "select distinct date_day as date_day, id from monitor_users where user_id='$userNameId' and date_day>='$realDayStart' group by date_day order by date_day";
			$mysqlConn->SetMakeQuery($query);
			%params = ();
			while($mysqlHash = $mysqlConn->GetHashrow()) {$params{$mysqlHash->{id}} = $mysqlHash->{date_day};}
			$htmlPage->CellSelect({"width" => "150", "classTd" => "normal", "classSelect" => "normal", "name" => "dateDayStop", "formName" => "thirdStep", "selId" => "$dateDayStop"},\%params);
			$mysqlConn->EndQuery();
		$htmlPage->EndRow();
		$htmlPage->StartRow();
			$htmlPage->CellButton({"classTd" => "headerLeft", "classButton" => "buttonInput100", "width" => "250", "colspan" => "2", "msg" => "Build Graph"});
		$htmlPage->EndRow();
		$htmlPage->HiddenVar({"name" => "action", "value" => "generateGraph"});
		$htmlPage->HiddenVar({"name" => "userNameId", "value" => "$userNameId"});
		$htmlPage->HiddenVar({"name" => "dateDayStart", "value" => "$dateDayStart"});
		$htmlPage->EndForm();
	}
}

sub StepOne
{
	my $userNameId = shift;
	my $dateDayStart = shift;
	my $query; my %params; my $mysqlHash; my $count = 0; 
	if(!$userNameId or $userNameId eq "---")
	{
		$htmlPage->StartRow();
			$htmlPage->Cell({"width" => "300", "class" => "headerWarning", "msg" => "Username NOT OK", "colspan" => "2"});
		$htmlPage->EndRow();
	}
	else
	{
		$htmlPage->StartRow();
			$htmlPage->StartForm({"name" => "secondStep", "method" => "post", "target" => "down"});
			$htmlPage->Cell({"width" => "100", "class" => "headerLeft", "msg" => "Start Date"});
			$query = "select distinct date_day as date_day,id from monitor_users where user_id='$userNameId' group by date_day order by date_day";
			$mysqlConn->SetMakeQuery($query);
			while($mysqlHash = $mysqlConn->GetHashrow()) {$params{$mysqlHash->{id}} = $mysqlHash->{date_day};}
			$mysqlConn->EndQuery();
			$htmlPage->CellSelect({"width" => "150", "classTd" => "normal", "classSelect" => "normal", "name" => "dateDayStart", "formName" => "secondStep", "selId" => "$dateDayStart"},\%params);
			$htmlPage->HiddenVar({"name" => "action", "value" => "stepTwo"});
			$htmlPage->HiddenVar({"name" => "userNameId", "value" => "$userNameId"});
			$htmlPage->EndForm();
		$htmlPage->EndRow();
	}
}

sub StepZero
{
	my $userNameId = shift;
	my $query; my %params; my $mysqlHash;
        $htmlPage->StartRow();
                $htmlPage->StartForm({"name" => "firstStep", "method" => "post", "target" => "down"});
                $htmlPage->Cell({"width" => "100", "class" => "headerLeft", "msg" => "UserName"});
                $query = "select username,common_name,id from users";
                $mysqlConn->SetMakeQuery($query);
                while($mysqlHash = $mysqlConn->GetHashrow()) {$params{$mysqlHash->{id}} = "$mysqlHash->{username} ($mysqlHash->{common_name})";}
                $mysqlConn->EndQuery();
                $htmlPage->CellSelect({"width" => "150", "classTd" => "normal", "classSelect" => "normal", "name" => "userNameId", "formName" => "firstStep", "selId" => "$userNameId"},\%params);
                $htmlPage->HiddenVar({"name" => "action", "value" => "stepOne"});
                $htmlPage->EndForm();
        $htmlPage->EndRow();
	
}
