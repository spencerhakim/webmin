#!/usr/local/bin/perl
# list_ifcs.cgi
# List active and boot-time interfaces

require './net-lib.pl';
&ReadParse();
$access{'ifcs'} || &error($text{'ifcs_ecannot'});
$allow_add = &can_create_iface() && !$noos_support_add_ifcs;
&ui_print_header(undef, $text{'ifcs_title'}, "");

# Show interfaces that are currently active
@act = &active_interfaces();
if (!$access{'bootonly'}) {
	# Table heading and links
	print &ui_subheading($text{'ifcs_now'});
	local @tds;
	@links = ( );
	if ($access{'ifcs'} >= 2) {
		print &ui_form_start("delete_aifcs.cgi", "post");
		push(@links, &select_all_link("d"),
			     &select_invert_link("d") );
		push(@tds, "width=5");
		}
	push(@tds, "width=20%", "width=20%", "width=20%", "width=20%");
	if ($allow_add) {
		push(@links,
		     "<a href='edit_aifc.cgi?new=1'>$text{'ifcs_add'}</a>");
		}
	print &ui_links_row(\@links);
	print &ui_columns_start([ $access{'ifcs'} >= 2 ? ( "" ) : ( ),
				  $text{'ifcs_name'},
				  $text{'ifcs_type'},
				  $text{'ifcs_ip'},
				  $text{'ifcs_mask'},
				  $text{'ifcs_status'} ], 100, 0, \@tds);

	# Show table of interfaces
	@act = sort iface_sort @act;
	foreach $a (@act) {
		next if ($access{'hide'} &&	# skip hidden
			 (!$a->{'edit'} || !&can_iface($a)));
		local $mod = &module_for_interface($a);
		local %minfo = $mod ? &get_module_info($mod->{'module'}) : ( );
		local @cols;
		if ($a->{'edit'} && &can_iface($a)) {
			push(@cols,
			    "<a href=\"edit_aifc.cgi?idx=$a->{'index'}\">".
			    &html_escape($a->{'fullname'})."</a>");
			}
		elsif (!$a->{'edit'} && $mod) {
			push(@cols,
			   "<a href=\"mod_aifc.cgi?idx=$a->{'index'}\">".
			   &html_escape($a->{'fullname'})."</a>");
			}
		else {
			push(@cols, &html_escape($a->{'fullname'}));
			}
		if ($a->{'virtual'} ne "") {
			$cols[0] = "&nbsp;&nbsp;".$cols[0];
			}
		push(@cols, &iface_type($a->{'name'}).
		      ($a->{'virtual'} eq "" ||
		       $mod ? "" : " ($text{'ifcs_virtual'})").
		      (%minfo ? " ($minfo{'desc'})" : ""));
		push(@cols, &html_escape($a->{'address'}));
		push(@cols, &html_escape($a->{'netmask'}));
		push(@cols, $a->{'up'} ? $text{'ifcs_up'} :
			"<font color=#ff0000>$text{'ifcs_down'}</font>");
		if ($a->{'edit'} && &can_iface($a)) {
			print &ui_checked_columns_row(\@cols, \@tds, "d",
						      $a->{'fullname'});
			}
		else {
			print &ui_columns_row([ "", @cols ], \@tds);
			}
		}
	print &ui_columns_end();
	print &ui_links_row(\@links);
	if ($access{'ifcs'} >= 2) {
		print &ui_form_end([ [ "delete", $text{'index_delete1'} ] ]);
		}
	print "<hr>\n";
	}

# Show interfaces that get activated at boot
print &ui_subheading($text{'ifcs_boot'});
print &ui_form_start("delete_bifcs.cgi", "post");
@links = ( &select_all_link("b", 1),
	   &select_invert_link("b", 1) );
if ($allow_add) {
	push(@links, "<a href='edit_bifc.cgi?new=1'>$text{'ifcs_add'}</a>");
	if (($gconfig{'os_type'} eq 'debian-linux') && (&has_command("ifenslave")))  {
		push(@links, "<a href='edit_bifc.cgi?new=1&bond=1'>$text{'bonding_add'}</a>");
	}
	if (($gconfig{'os_type'} eq 'debian-linux') && (&has_command("vconfig")))  {
		push(@links, "<a href='edit_bifc.cgi?new=1&vlan=1'>$text{'vlan_add'}</a>");
	}
	}
if ($allow_add && defined(&supports_ranges) && &supports_ranges()) {
	push(@links, "<a href='edit_range.cgi?new=1'>$text{'ifcs_radd'}</a>");
	}
print &ui_links_row(\@links);
@tds = ( "width=5", "width=20%", "width=20%", "width=20%",
	 "width=20%", "width=20%");
print &ui_columns_start([ "",
			  $text{'ifcs_name'},
			  $text{'ifcs_type'},
			  $text{'ifcs_ip'},
			  $text{'ifcs_mask'},
			  $text{'ifcs_act'} ], 100, 0, \@tds);

@boot = &boot_interfaces();
@boot = sort iface_sort @boot;
foreach $a (@boot) {
	local $can = $a->{'edit'} && &can_iface($a);
	next if ($access{'hide'} && !$can);	# skip hidden
	local @cols;
	local @mytds = @tds;
	if ($a->{'range'} ne "") {
		# A range of addresses
		local $rng = &text('ifcs_range', $a->{'range'});
		if ($can && ($gconfig{'os_type'} eq 'debian-linux') && &has_command("")) {
			$link = "edit_bifc.cgi?idx=$a->{'index'}";
			if(&iface_type($a->{'name'}) eq 'Bonded'){
				$link = $link . "&bond=1";
			} elsif (&iface_type($a->{'name'}) =~ /^(.*) (VLAN)$/) {
				$link = $link . "&vlan=1";
			}
			push(@cols, "<a href='$link'" . &html_escape($a->{'fullname'})."</a>");
			}
		elsif($can) {
			$link = "edit_bifc.cgi?idx=$a->{'index'}";
			push(@cols, "<a href='$link'" . &html_escape($a->{'fullname'})."</a>");
		}
		else {
			push(@cols, &html_escape($rng));
			}
		push(@cols, &iface_type($a->{'name'}));
		push(@cols, "$a->{'start'} - $a->{'end'}");
		splice(@mytds, 3, 2, "colspan=2 width=40%");
		}
	else {
		# A normal single interface
		local $mod = &module_for_interface($a);
		local %minfo = $mod ? &get_module_info($mod->{'module'}) : ( );
		if ($can) {
			$link = "edit_bifc.cgi?idx=$a->{'index'}";
			if(&iface_type($a->{'name'}) eq 'Bonded'){
				$link = $link . "&bond=1";
			} elsif (&iface_type($a->{'name'}) =~ /^(.*) (VLAN)$/) {
				$link = $link . "&vlan=1";
			}
			push(@cols, "<a href='$link'>"
				    .&html_escape($a->{'fullname'})."</a>");
			}
		else {
			push(@cols, &html_escape($a->{'fullname'}));
			}
		if ($a->{'virtual'} ne "") {
			$cols[0] = "&nbsp;&nbsp;".$cols[0];
			}
		push(@cols, &iface_type($a->{'name'}).
		     ($a->{'virtual'} eq "" ||
		      $mod ? "" : " ($text{'ifcs_virtual'})").
		     (%minfo ? " ($minfo{'desc'})" : ""));
		push(@cols, $a->{'bootp'} ? $text{'ifcs_bootp'} :
			    $a->{'dhcp'} ? $text{'ifcs_dhcp'} :
			    $a->{'address'} ? &html_escape($a->{'address'}) :
					       $text{'ifcs_auto'});
		push(@cols, $a->{'netmask'} ? &html_escape($a->{'netmask'})
					    : $text{'ifcs_auto'});
		}
	push(@cols, $a->{'up'} ? $text{'yes'} : $text{'no'});
	if ($can) {
		print &ui_checked_columns_row(\@cols, \@mytds, "b",
					      $a->{'fullname'});
		}
	else {
		print &ui_columns_row([ "", @cols ], \@tds);
		}
	}
print &ui_columns_end();
print &ui_links_row(\@links);
print &ui_form_end([ [ "delete", $text{'index_delete2'} ],
		     [ "deleteapply", $text{'index_delete3'} ],
		     undef,
		     [ "apply", $text{'index_apply2'} ] ]);

&ui_print_footer("", $text{'index_return'});

sub iface_sort
{
return $a->{'name'} cmp $b->{'name'} if ($a->{'name'} cmp $b->{'name'});
return $a->{'virtual'} eq '' ? -1 :
       $b->{'virtual'} eq '' ? 1 : $a->{'virtual'} <=> $b->{'virtual'};
}

