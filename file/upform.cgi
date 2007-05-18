#!/usr/local/bin/perl
# upform.cgi
# Display the upload form

require './file-lib.pl';
$disallowed_buttons{'upload'} && &error($text{'ebutton'});
&ReadParse(undef, undef, 1);
&popup_header($text{'upload_title'});
$upid = time().$$;
$args = ($in{'extra'} ? $in{'extra'}."&" : "?")."id=$upid";

print &ui_form_start("upload.cgi$args", "form-data", undef,
		     &read_parse_mime_javascript($upid, [ "file" ]));
print &ui_table_start($text{'upload_title'}, "width=100%", 2);

print &ui_table_row($text{'upload_file'},
		    &ui_upload("file", 20));

print &ui_table_row($text{'upload_dir'},
		    &ui_textbox("dir", $in{'dir'}, 20)."\n".
		    &ui_submit($text{'upload_ok'}));

if ($dostounix == 1) {
	# Do DOS conversion?
	print &ui_table_row($text{'upload_conv'},
			    &ui_yesno_radio("dos", 0));
	}

if ($unarchive == 1) {
	# Unzip file?
	print &ui_table_row($text{'upload_zip'},
			    &ui_radio("zip", 0,
				[ [ 2, $text{'upload_yes'} ],
				  [ 1, $text{'yes'} ],
				  [ 0, $text{'no'} ] ]));
	}

if ($running_as_root) {
	# Upload as user
	print &ui_table_row($text{'upload_user'},
			    &ui_user_textbox("user", "root"));
	}

print &ui_table_end();
print &ui_form_end();
&popup_footer();

