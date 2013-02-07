
sub GetData
{
        my @time = localtime(time());
        $time[4] = $time[4] + 1;         ##luna
        $time[5] = $time[5] + 1900;      ##anul
        if($time[4] < 9) {$time[4] = "0$time[4]";}
        if($time[3] < 9) {$time[3] = "0$time[3]";}
        my $timp = "$time[5]-$time[4]-$time[3]";
        return $timp;
}

sub GetTime
{
        my @time = localtime(time());
        if($time[0] < 10) {$time[0] = "0$time[0]";}
        if($time[1] < 10) {$time[1] = "0$time[1]";}
        my $timp = "$time[2]:$time[1]:$time[0]";
        return $timp;
}

sub SendMail
{
        my ($self,$destunu,$destdoi,$source,$subject,$mesage,$path,$filename,$type) = @_;
        use MIME::Lite;
        my $message = MIME::Lite->new(
        From     => "$source",
        To       => "$destunu",
        Cc      => "$destdoi",
        Subject  => "$subject",
        Type     => "multipart/mixed");
        $message->attach(
        Type    => 'text/html',
        Data    => "$mesage");
        if(!$type) {$type = "xls";}
        if($path and $filename)
        {
                $message->attach(
                Type    => "aplication/$type",
                Disposition => "attachment",
                Path    => "$path",
                Filename => "$filename");
        }
        $message->send;
}

return 1;
