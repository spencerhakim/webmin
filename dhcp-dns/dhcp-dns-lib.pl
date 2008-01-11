# Functions for configuring DNS and DHCP servers together

do '../web-lib.pl';
&init_config();
do '../ui-lib.pl';
&foreign_require("bind8", "bind8-lib.pl");
&foreign_require("dhcpd", "dhcpd-lib.pl");

# list_dhcp_hosts()
# Returns a list of DHCP host structures for managed hosts
sub list_dhcp_hosts
{
local $conf = &dhcpd::get_config();
local $parent = &dhcpd::get_parent_config();
local @rv;
foreach my $h (&dhcpd::find("host", $conf)) {
	$h->{'parent'} = $parent;
	push(@rv, $h);
	}
foreach my $g (&dhcpd::find("group", $conf)) {
	foreach my $h (&dhcpd::find("host", $g->{'members'})) {
		$h->{'parent'} = $g;
		push(@rv, $h);
		}
	}
foreach my $s (&dhcpd::find("subnet", $conf)) {
	foreach my $h (&dhcpd::find("host", $s->{'members'})) {
		$h->{'parent'} = $s;
		push(@rv, $h);
		}
	foreach my $g (&dhcpd::find("group", $s->{'members'})) {
		foreach my $h (&dhcpd::find("host", $g->{'members'})) {
			$h->{'parent'} = $g;
			push(@rv, $h);
			}
		}
	}
return @rv;
}

# host_form([&host])
# Returns a form for editing or creating a host
sub host_form
{
local ($h) = @_;
local $new = !$h;
local $rv;
$rv .= &ui_form_start("save.cgi", "post");
if ($new) {
	$rv .= &ui_hidden("new", 1);
	}
else {
	$rv .= &ui_hidden("old", $h->{'values'}->[0]);
	}
$rv .= &ui_table_start($text{'form_header'}, "width=100%", 2);

# Hostname
local $short = &short_hostname($h->{'values'}->[0]);
local $indom = $new || $short ne $h->{'values'}->[0];
$rv .= &ui_table_row($text{'form_host'},
	&ui_textbox("host", $short, 20).
	($indom ? "<tt>.$config{'domain'}</tt>" : ""));
$rv .= &ui_hidden("indom", $indom);

# Fixed IP address
local $fixed = &dhcpd::find("fixed-address", $h->{'members'});
$rv .= &ui_table_row($text{'form_ip'},
	&ui_textbox("ip", $fixed ? $fixed->{'values'}->[0] : undef, 20));

# MAC address
local $hard = &dhcpd::find("hardware", $h->{'members'});
$rv .= &ui_table_row($text{'form_mac'},
	&ui_select("media", $hard ? $hard->{'values'}->[0] : "ethernet",
		   [ [ "ethernet", $text{'form_ethernet'} ],
		     [ "token-ring", $text{'form_tr'} ],
		     [ "fddi", $text{'form_fddi'} ] ], 1, 0, 1).
	&ui_textbox("mac", $hard ? $hard->{'values'}->[1] : undef, 20));

$rv .= &ui_table_end();
if ($new) {
	$rv .= &ui_form_end([ [ undef, $text{'create'} ] ]);
	}
else {
	$rv .= &ui_form_end([ [ undef, $text{'save'} ],
			      [ 'delete', $text{'delete'} ] ]);
	}
return $rv;
}

sub short_hostname
{
local ($hn) = @_;
if ($hn =~ /^(\S+)\.\Q$config{'domain'}\E$/) {
	return $1;
	}
else {
	return $hn;
	}
}

# get_dns_zone()
# Returns the records file and list of records for the domain
sub get_dns_zone
{
local $conf = &bind8::get_config();
local @zones = &bind8::find("zone", $conf);
foreach my $v (&bind8::find("view", $conf)) {
	push(@zones, &bind8::find("zone", $v->{'members'}));
	}
local ($z) = grep { lc($_->{'value'}) eq lc($config{'domain'}) } @zones;
return ( ) if (!$z);
local $file = &bind8::find("file", $z->{'members'});
local $fn = $file->{'values'}->[0];
local @recs = &bind8::read_zone_file($fn, $config{'domain'});
return ( $fn, \@recs );
}

sub apply_configuration
{
&dhcpd::restart_dhcpd();
&bind8::restart_bind();
}

1;

