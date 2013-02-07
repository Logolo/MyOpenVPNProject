#!/usr/bin/perl

use lib "modules";
use HtmlObject;

my $htmlPage; my %params = ();

###############################################################################
$htmlPage = HtmlObject->new();
%params = ("pageTitle" => "OpenVPN Mng", "cssStyle" => "style.css");
$htmlPage->StartPage(\%params);
%params = ("width" => "300", "align" => "left", "cellpadding" => "2");
$htmlPage->StartTable(\%params);
$htmlPage->StartRow();
	%params = ("name" => "usersButton", "method" => "post" => "target" => "down", "action" => "users.cgi");
	$htmlPage->StartForm(\%params);
	%params = ("width" => "100", "align" => "left", "classTd" => "headerTitle", "classButton" => "buttonInput100", "msg" => "Users");
	$htmlPage->CellButton(\%params);
	$htmlPage->EndForm();
	#####################
	%params = ("name" => "generalButton", "method" => "post" => "target" => "down", "action" => "general.cgi");
	$htmlPage->StartForm(\%params);
	%params = ("width" => "100", "align" => "left", "classTd" => "headerTitle", "classButton" => "buttonInput100", "msg" => "Vpn Server");
	$htmlPage->CellButton(\%params);
	$htmlPage->EndForm();
	####################
	%params = ("name" => "graficeButton", "method" => "post" => "target" => "down", "action" => "grafice.cgi");
	$htmlPage->StartForm(\%params);
	%params = ("width" => "100", "align" => "left", "classTd" => "headerTitle", "classButton" => "buttonInput100", "msg" => "Grafice");
	$htmlPage->CellButton(\%params);
	$htmlPage->EndForm();
	######################
	##facem butoane	
$htmlPage->EndRow();
$htmlPage->EndTable();
$htmlPage->ClearAll();
$htmlPage->TheHR();
$htmlPage->EndPage();
###############################################################################
