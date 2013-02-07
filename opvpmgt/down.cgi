#!/usr/bin/perl

use lib "modules";
use HtmlObject;

my $htmlPage; my %params = ();

###############################################################################
$htmlPage = HtmlObject->new();
%params = ("pageTitle" => "OpenVPN Mng", "cssStyle" => "style.css");
$htmlPage->StartPage(\%params);
%params = ("width" => "300", "align" => "left");
$htmlPage->StartTable(\%params);
$htmlPage->StartRow();
        ##facem butoane
$htmlPage->EndRow();
$htmlPage->EndTable();
$htmlPage->EndPage();
###############################################################################

