package PostVars;

sub new
{
        my $class = shift;
        my $self = {}; 
        $self->{pageTitle} = undef;
        $self->{cssStyle} = undef;
	$self->{vars} = undef;
        bless($self,$class);
	$self->{vars};
	my $textVars; my @parts; my $part;
        read( STDIN, $tmpStr, $ENV{ "CONTENT_LENGTH" } );
        @parts = split( /\&/, $tmpStr );
        foreach $part (@parts)
        {
                my ($name, $value) = split(/\=/,$part);
                $value =~ ( s/%23/\#/g );
                $value =~ ( s/%2F/\//g );
                $self->{vars}->{"$name"} = $value;
        }
	return $self;
}

sub GetVar
{
	my $self = shift;
	my $params = shift;
	my $varName = $params->{varName};
	my $varHash = $self->{vars};
	my $var = $varHash->{$varName};
	$var = CleanTextVariable($var);
	return $var;
}

sub GetVarSingle
{
        my $self = shift;
        my $varName = shift;
        my $varHash = $self->{vars};
        my $var = $varHash->{$varName};
        $var = CleanTextVariable($var);
        return $var;
}

sub CleanTextVariable
{
        my $textVar = shift(@_);
        $textVar =~ s/[+]/ /g;
        $textVar =~ s/%3B/;/g;
        $textVar =~ s/%0D%0A/<BR>/g;
        $textVar =~ s/%3CBR%3E/<BR>/g;
        $textVar =~ s/%3A/:/g;
        $textVar =~ s/%2B/+/g;
        $textVar =~ s/%2C/,/g;
        $textVar =~ s/%26/&/g;
        $textVar =~ s/%28/(/g;
        $textVar =~ s/%29/)/g;
        $textVar =~ s/%3E/>/g;
        $textVar =~ s/%22/"/g;
        $textVar =~ s/%3F/?/g;
        $textVar =~ s/%21/!/g;
        $textVar =~ s/%3C/</g;
        $textVar =~ s/%09/ /g;
        $textVar =~ s/%3D/=/g;
	$textVar =~ s/%40/@/g;
        return $textVar;
}

sub GetUser
{
        my $user=$ENV{REMOTE_USER};
        if ( $user =~ /^\s*$/ ) {return "";}
        return $user;
}

return 1;
