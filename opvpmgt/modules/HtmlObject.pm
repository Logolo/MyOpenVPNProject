package HtmlObject;
use strict;

sub new
{
	my $class = shift;
	my $self = {};
	$self->{pageTitle} = undef;
	$self->{cssStyle} = undef;
	bless($self,$class);
	return $self;
}

sub StartPage
{
	my $self = shift;
	my $params = shift;
	my $htmlText = undef;
	my $pageTitle = $params->{pageTitle};
	my $cssStyle = $params->{cssStyle};
	my $background = $params->{background};
	if($pageTitle) {$pageTitle = "<title>$pageTitle</title>";}
	else {$pageTitle = "";}
	if($cssStyle) {$cssStyle = "<LINK REL=stylesheet TYPE='text/css' HREF='$cssStyle'>";}
	else {$cssStyle = "";}
	if($background) {$background = "background='$background'";}
	else {$background = "";}
	$htmlText = "Content-type: text/html\n\n
	<html><head>
        $pageTitle
        $cssStyle
        </head> <body $background>";
	print "$htmlText";
}

sub EndPage
{
	my $self = shift;
	my $textTemp = "</body>";
	print "$textTemp";
}

sub StartTable
{
        my $self = shift;
        my $params = shift;
        my $width = $params->{width};
        my $align = $params->{align};
        my $cellspacing = $params->{cellspacing};
        my $cellpadding = $params->{cellpadding};
	my $class = $params->{class};
	if($width) {$width = "width='$width'";}
	else {$width = "";}
	if($class) {$class = "class='$class'";}
	else {$class = "";}
	if($cellpadding) {$cellpadding = "cellpadding='$cellpadding'";}
	else {$cellpadding = "cellpadding='0'";}
	if($cellspacing) {$cellspacing = "cellspacing='$cellspacing'";}
	else {$cellspacing = "cellspacing='0'";}
	if($align) {$align = "align='$align'";}
	else {$align = "";}
        my $textTemp = "<table $align $width $class $cellspacing $cellpadding>";
	print $textTemp;
}

sub EndTable
{
        my $self = shift;
        my $textTemp = "</table>";
	print $textTemp;
}

sub ClearAll
{
	my $self = shift;
	my $textTemp = "<br clear='all'>";
	print "$textTemp";
}

sub TheHR
{
	my $self = shift;
	my $params = shift;
	my $count = $params->{count};
	my $class = $params->{class};
	if(!$count) {$count = 1;}
	if($class) {$class = "class='$class'";}
	else {$class = "";}
	my $textTemp = "<hr $class>";
	print "$textTemp";
}

sub TheBR
{
        my $self = shift;
	my $count = shift;
	if(!$count) {$count = 1;}
	my $i; my $textTemp = "";
	for($i=0;$i<$count;$i++)
	{
		$textTemp .= "<br>";
	}
        print "$textTemp";
}

sub StartRow
{
	my $self = shift;
	my $params = shift;
	my $width = $params->{width};
	my $class = $params->{class};
	if($width) {$width = "width='$width'";}
	else {$width = "";}
	if($class) {$class = "class='$class'";}
	else {$class="";}
	my $tempText = "<tr $width $class>";
	print $tempText;
}

sub EndRow
{
	my $self = shift;
	my $params = shift;
	my $tempText = "</tr>";
	print $tempText;
}

sub Cell
{
        my $self = shift;
        my $params = shift;
        my $width = $params->{width};
        my $class = $params->{class};
        my $colspan = $params->{colspan};
        my $msg = $params->{msg};
	my $height = $params->{height};
        if(!$msg) {$msg = " ";}
        if($width) {$width = "width='$width'";}
        else {$width = "";}
        if($class) {$class = "class='$class'";}
        else {$class = "";}
        if($colspan) {$colspan = "colspan='$colspan'";}
        else {$colspan = "";}
	if($height) {$height = "height='$height'";}
	else {$height = "";}
        my $textTemp = "<td $class $width $height $colspan>$msg</td>";
	print $textTemp;
}

sub CellSelect
{
	my $self = shift;
	my $params = shift;
	my $hashRef = shift;
	my $textTemp = "";
	my $width = $params->{width};
	my $classTd = $params->{classTd};
	my $classSelect = $params->{classSelect};
	my $colspan = $params->{colspan};
	my $height = $params->{height};
	my $name = $params->{name};
	my $formName = $params->{formName};
	my $selId = $params->{selId};
	my $multiple = $params->{multiple};
	my $orderByValue = $params->{orderByValue};
	if($width) {$width = "width='$width'";}
	else {$width = "";}
	if($classTd) {$classTd = "class='$classTd'";}
	else {$classTd = "";}
	if($colspan) {$colspan = "colspan='$colspan'";}
	else {$colspan = "";}
	if($height) {$height = "height='$height'";}
	else {$height = "";}
	if($classSelect) {$classSelect = "class=$classSelect";}
	else {$classSelect = "";}
	if($name) {$name = "name=$name";}
	else {$name = "";}
	if($formName) {$formName = "onChange='$formName.submit()'";}
	else {$formName = "";}
	if($multiple) {$multiple = "multiple";}
	else {$multiple = "";}
	$textTemp = "<td $classTd $width $colspan>";
	$textTemp .= "<select $name $classSelect $formName>
	<option value='---'>---</option>
	";
	my $i; my @keys; my $key; my $count;
	if(!$selId or $selId == 0)
	{
		if(!$orderByValue or $orderByValue == 0)
		{
			foreach $key (sort {$hashRef->{$a} cmp $hashRef->{$b}} keys %$hashRef) 
			{	
				$textTemp .= "<option value='$key'>$$hashRef{$key}</option>";
			}
		}
		else
		{
			@keys = sort {$a <=> $b} keys %$hashRef;
			$count = @keys;
			for($i=0;$i<$count;$i++){$textTemp .= "<option value='$keys[$i]'>$$hashRef{$keys[$i]}</option>";}
		}
	}
	else
	{
		if(!$orderByValue or $orderByValue == 0)	
		{
			foreach $key (sort {$hashRef->{$a} cmp $hashRef->{$b}} keys %$hashRef)
			{
				if($selId == $key) {$textTemp .= "<option selected value='$key'>$$hashRef{$key}</option>";}
				else {$textTemp .= "<option value='$key'>$$hashRef{$key}</option>";}
			}
		}
		else
		{
			@keys = sort {$a <=> $b} keys %$hashRef;
			$count = @keys;
			for($i=0;$i<$count;$i++)
			{
				if($selId == $keys[$i]) {$textTemp .= "<option selected value='$keys[$i]'>$$hashRef{$keys[$i]}</option>";}
				else {$textTemp .= "<option value='$keys[$i]'>$$hashRef{$keys[$i]}</option>";}
			}
		}
	}
	$textTemp .= "</selected></td>";
	print "$textTemp";
}

sub CellInput
{
        my $self = shift;
        my $params = shift;
        my $width = $params->{width};
        my $classTd = $params->{classTd};
        my $classInput = $params->{classInput};
        my $colspan = $params->{colspan};
        my $name = $params->{name};
        my $type = $params->{type};
        my $maxLenght = $params->{maxLenght};
        my $disable = $params->{disable};
	my $value = $params->{value};	
	if($width) {$width = "width='$width'";}
	else {$width = "";}
	if($classTd) {$classTd = "class='$classTd'";}
        else {$classTd = "";}
	if($classInput) {$classInput = "class='$classInput'";}
        else {$classInput = "";}
	if($colspan) {$colspan = "colspan='$colspan'";}
        else {$colspan = "";}
	if($name) {$name = "name='$name'";}
        else {$name = "";}
	if($type) {$type = "type='$type'";}
        else {$type = "";}
	if($maxLenght) {$maxLenght = "maxlength='$maxLenght'";}
        else {$maxLenght = "";}
	if($disable) {$disable = "disable";}
        else {$disable = "";}
	if($value) {$value = "value='$value'";}
        else {$value = "";}
	my $textTemp = "<td $classTd $width $colspan>
	<input $type $classInput $name $maxLenght $value $disable>
	</td>";
	print "$textTemp";
}


sub CellTextarea
{
        my $self = shift;
        my $params = shift;
        my $width = $params->{width};
        my $classTd = $params->{classTd};
        my $classInput = $params->{classInput};
        my $colspan = $params->{colspan};
        my $name = $params->{name};
	my $value = $params->{value};
	my $cols = $params->{cols};
	my $rows = $params->{rows};
	my $disable = $params->{disable};
	if($width) {$width = "width='$width'";}
	else {$width = "";}
	if($classTd) {$classTd = "class='$classTd'";}
        else {$classTd = "";}
	if($classInput) {$classInput = "class='$classInput'";}
        else {$classInput = "";}
	if($colspan) {$colspan = "colspan='$colspan'";}
        else {$colspan = "";}
	if($name) {$name = "name='$name'";}
        else {$name = "";}
        if($cols) {$cols = "cols='$cols'";}
        else {$cols = "";}
        if($rows) {$rows = "rows='$rows'";}
        else {$rows = "";}
        if($disable) {$disable = "disable";}
        else {$disable = "";}
	my $textTemp = "
	<td $classTd $width $colspan>
	<textarea $rows $cols $classInput $name $disable>$value</textarea>
	</td>
	";
	print "$textTemp";
}

sub CellButton
{
        my $self = shift;
        my $params = shift;
        my $width = $params->{width};
        my $classTd = $params->{classTd};
	my $msg = $params->{msg};
	my $colspan = $params->{colspan};
	my $classButton = $params->{classButton};
        if($width) {$width = "width='$width'";}
        else {$width = "";}
        if($classTd) {$classTd = "class='$classTd'";}
        else {$classTd = "";}
        if($colspan) {$colspan = "colspan='$colspan'";}
        else {$colspan = "";}
	if($classButton) {$classButton = "class='$classButton'";}
	else {$classButton = "";}
	if($msg) {$msg = "value='$msg'";}
	else {$msg = "";}
	my $textTemp = "<td $classTd $width $colspan>
	<input type=submit $classButton $msg>
	</td>";
	print $textTemp;	
}

sub CellImage
{
        my $self = shift;
        my $params = shift;
        my $width = $params->{width};
        my $classTd = $params->{classTd};
        my $src = $params->{src};
        my $name = $params->{name};
        my $height = $params->{height};
	my $colspan = $params->{colspan};
        if($width) {$width = "width='$width'";}
        else {$width = "";}
        if($classTd) {$classTd = "class='$classTd'";}
        else {$classTd = "";}
        if($colspan) {$colspan = "colspan='$colspan'";}
        else {$colspan = "";}
	if($name) {$name = "name='$name'";}
        else {$name = "";}
	if($height) {$height = "height='$height'";}
	else {$height = "";}
	if($src) {$src = "src='$src'";}
	else {$src = "src=none";}
	my $textTemp = "<td $width $height $classTd>
	<img $src>
	</td>
	";
	print $textTemp;	
}

sub CellImageButton
{
	my $self = shift;
	my $params = shift;
        my $width = $params->{width};
        my $classTd = $params->{classTd};
	my $src = $params->{src};
	my $name = $params->{name};
	my $height = $params->{height};
	my $colspan = $params->{colspan};
	if($height) {$height = "height='$height'";}
        if($src) {$src = "src='$src'";}
        if($width) {$width = "width='$width'";}
        if($classTd) {$classTd = "class='$classTd'";}
        if($colspan) {$colspan = "colspan='$colspan'";}
        if($name) {$name = "name='$name'";}
	my $textTemp = "<td $width $height $classTd $colspan>
	<input type=image $src $name $height $width></td>";
	print $textTemp;	
}

sub CellLink
{
        my $self = shift;
        my $params = shift;
        my $width = $params->{width};
	my $height = $params->{height};
	my $classTd = $params->{classTd};
	my $classHref = $params->{classHref};
	my $classImg = $params->{classImg};
	my $href = $params->{href};	
	my $colspan = $params->{colspan};
	my $img = $params->{img};
	my $text = $params->{text};
	if($width) {$width = "width='$width'";}
	if($classTd) {$classTd = "class='$classTd'";}
	if($colspan) {$colspan = "colspan='$colspan'";}
	if($classHref) {$classHref = "class='$classHref'";}
	my $textTemp = "<td $width $colspan $classTd>
	<a href='$href' $classHref>$text";
	if($img) {$textTemp .= "<img src='$img' border=none></img>";}
	$textTemp .= "</a></td>";	
	print $textTemp;
}

sub Header
{
        my $self = shift;
        my $params = shift;
        my $width = $params->{width};
        my $class = $params->{class};
	my $msg = $params->{msg};
	my $align = $params->{align};
	my $height = $params->{height};
	my $width = $params->{width};
	my $tempText = "
	<table width=$width align=$align width=$width height=$height cellpadding=0 cellspacing=0>
	<tr>
	<td class=$class>$msg</td>
	</tr>
	</table>
	";
	print "$tempText";	
}

sub StartForm
{
        my $self = shift;
        my $params = shift;
	my $name = $params->{name};
	my $method = $params->{method};
	my $action = $params->{action};
	my $target = $params->{target};
	my $tempText = "<form name=$name method=$method";
	if($target) {$tempText .= " target=$target";}
	if($action) {$tempText .= " action=$action";}
	$tempText .= ">";
	print $tempText;
}

sub EndForm
{
	my $self = shift;
	my $tempText = "</form>";
	print $tempText;
}

sub HiddenVar
{
	my $self = shift;
	my $params = shift;
	my $name = $params->{name};
	my $value = $params->{value};
	my $tempText = "<input type=hidden name='$name' value='$value'>";
	print $tempText;
}

return 1;
