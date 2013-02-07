package MysqlConnection;
use strict;
use DBI;

sub new 
{
	my $class = shift;
	my $self = {};
	$self->{host} = "127.0.0.1";
	$self->{user} = "openvpn";
	$self->{pass} = "openvpn";
	$self->{database} = "openvpn";
	$self->{query} = undef;
	$self->{queryDth} = undef;
	$self->{querySth} = undef;
	$self->{result} = undef;	
	$self->{dbh} = undef;
	$self->{sth} = undef;
	$self->{dth} = undef;
	$self->{tth} = undef;
	bless($self,$class);
	return $self;
}

sub GetHost
{
	my $self = shift;
	return $self->{host};
}

sub GetUser
{
	my $self = shift;
	return $self->{user};
}

sub GetPass
{
	my $self = shift;
	return $self->{pass};
}

sub GetDatabase
{
	my $self = shift;
	return $self->{database};
}

sub GetQuery
{
	my $self = shift;
	return $self->{query};
}

sub GetDbh
{
	my $self = shift;
	return $self->{dbh};
}

sub GetSth
{
	my $self = shift;
	return $self->{sth};
}

sub GetColCount
{
	my $self = shift;
	my $sth = $self->{sth};
	my $count = 0;
	while($sth->fetchrow_hashref()) {$count++;}
	return $count;
}

sub GetHashrow
{
	my $self = shift;
	my $sth = $self->{sth};
	my $hashRef = $sth->fetchrow_hashref();
	return $hashRef;
}

sub GetHashrowSecondary
{
	my $self = shift;
	my $dth = $self->{dth};
	my $hashref = $dth->fetchrow_hashref();
	return $hashref;
}

sub GetHashrowThird
{
	my $self = shift;
	my $tth = $self->{tth};
	my $hashref = $tth->fetchrow_hashref();
	return $hashref;
}

sub SetHost
{
	my $self = shift;
	my $setHost = shift;
	$self->{host} = $setHost;
}

sub SetUser
{
	my $self = shift;
	my $setUser = shift;
	$self->{user} = $setUser;
}

sub SetPass
{
	my $self = shift;
	my $setPass = shift;
	$self->{pass} = $setPass;
}

sub SetDatabase
{
	my $self = shift;
	my $setDatabase = shift;
	$self->{database} = $setDatabase;
}

sub SetQuery
{
	my $self = shift;
	my $setQuery = shift;
	$self->{query} = $setQuery;
}

sub StartConnection
{
	my $self = shift;
	my $resultText;
	$self->{dbh} = DBI->connect("DBI:mysql:$self->{database};host=$self->{host}","$self->{user}","$self->{pass}");
	if(!$self->{dbh}) {return 10;} ## connection NOT OK
	else {return 1;} ## connection OK
}

sub StopConnection
{
	my $self = shift;
	my $dbh = $self->{dbh};
	$dbh->disconnect();
}

sub SetMakeQuery
{
	my $self = shift;
	my $setQuery = shift;
	my $dbh = $self->{dbh};
	$self->{query} = $setQuery;
	my $query = $self->{query};
	my $sth = $dbh->prepare($query) or die ("Error in creating mysql prepare");
	if(!$sth) {return "Query nu s-a putut executa";}
	else
	{
		$sth->execute() or die ("error in execute stamente");
		$self->{sth} = $sth;
		return 1;
	}
}

sub SetMakeQuerySecondary
{
	my $self = shift;
	my $setQuery = shift;
	my $dbh = $self->{dbh};
	$self->{queryDth} = $setQuery;
	my $query = $self->{queryDth};
	my $dth = $dbh->prepare($query) or die ("Error in creating mysql prepare");
	if(!$dth) {return "Query nu s-a putut executa";}
	else
	{
		$dth->execute() or die ("error in execute stamente");
		$self->{dth} = $dth;
		return 1;
	}
}

sub SetMakeQueryThird
{
	my $self = shift;
	my $setQuery = shift;
	my $dbh = $self->{dbh};
	$self->{querySth} = $setQuery;
	my $query = $self->{querySth};
	my $tth = $dbh->prepare($query) or die ("Error in creating mysql prepare");
	if(!$tth) {return "Query nu s-a putut executa";}
	else
	{
		$tth->execute() or die ("error in execute stamente");
		$self->{tth} = $tth;
		return 1;
	}

}

sub ReactivateCurrentQuery
{
	my $self = shift;
	my $sth = $self->{sth};
	my $query = $self->{query};
	my $dbh = $self->{dbh};
	$sth->finish();
	$sth = $dbh->prepare($query) or die ("Error in creating mysql prepare");
	if(!$sth) {return "Query nu s-a putut executa";}
	else
	{
		$sth->execute() or die ("error in execute stamente");
		$self->{sth} = $sth;
		return 1;
	}
}

sub EndQuery
{
	my $self = shift;
	my $sth = $self->{sth};
	$sth->finish();
}

sub EndQuerySecondary
{
	my $self = shift;
	my $dth = $self->{dth};
	$dth->finish();
}

sub EndQueryThird
{
	my $self = shift;
	my $tth = $self->{tth};
	$tth->finish();
}

return 1;
