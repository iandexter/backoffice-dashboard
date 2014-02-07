#!/usr/bin/perl
#
# Web service to get ERP messages through broker.

use strict;
use warnings;

use Net::OpenSSH;
use JSON;
use CGI qw(:standard);

our $VERSION = '0.5';

my $ssh;
my $json = JSON->new->allow_nonref;
my $cgi  = CGI->new;

my $threshold = param('threshold') || 15;
my $debug     = param('debug')     || 0;

# $Net::OpenSSH::debug = -1;

sub connect_ssh {
    my ($rhost) = @_;
    $ssh = Net::OpenSSH->new($rhost);
    $ssh->error && die "Unable to connect to $rhost: " . $ssh->error . "\n";
    return $ssh->get_ctl_path;
}

sub remote_command {
    my ( $rcmd, @input ) = @_;
    my $output =
      $ssh->capture( { stdin_data => \@input, stderr_to_stdout => 1 }, $rcmd );
    return $output;
}

### main()

my $rhost = 'broker.domain.org';
my $rcmd  = '/path/to/check_erp_msgs -n -t ' . $threshold;
if ($debug) { $rcmd .= ' -d'; }

connect_ssh($rhost);
my $output = remote_command($rcmd);

my %hash;
my @lines = split /\n/mx, $output;
if ( scalar @lines ) {
    foreach my $line (@lines) {
        my ( $k, $v ) = split /;/mx, $line;
        my @array = split /,/mx, $v;
        $hash{$k} = \@array;
    }
} else {
    $hash{'none'} = ['No incoming messages.'];
}

print $cgi->header('application/json');
print $json->pretty->encode( \%hash );
