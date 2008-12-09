<?php
/*
Common.php
Common datas and functions for Magnus' toys
(c) 2006 by Magnus Manske
Released under GPL
*/

ob_start("ob_gzhandler");

# Default settings
$is_on_toolserver = false ;
$nameofthetool = '' ;
$service_keys = array () ;

# Include local settings, if any
@include_once ( "local.php" ) ;

require_once ( "common_data.php" ) ;
require_once ( "class_imagedata.php" ) ;
require_once ( "class_pagedata.php" ) ;
require_once ( "class_wikiquery.php" ) ;
require_once ( "database_functions.php" ) ;


# Functions

function ansi2ascii($string, $repl = '_') {
  global $ansi2ascii ;
  foreach ( $ansi2ascii AS $k => $v )
    $string = str_replace ( $k , $v , $string ) ;
  for ($n = 0; $n < strlen($string); $n++) {
    if (ord($string{$n}) > 127) $string{$n} = $repl;
  }
  return $string ;
}


function get_tool_name () {
	global $nameofthetool ;
	if ( $nameofthetool == '' ) return '' ;
	return " /* This query is presented to you by {$nameofthetool}, courtesy of Magnus Manske */ " ;
}

function microtime_float()
{
   list($usec, $sec) = explode(" ", microtime());
   return ((float)$usec + (float)$sec);
}

function myflush () {
	 @ob_flush();
     flush();
}

function myurlencode ( $t ) {
	$t = str_replace ( " " , "_" , $t ) ;
	$t = urlencode ( $t ) ;
	return $t ;
}

function strip_html_comments ( &$text ) {
	return preg_replace( '?<!--.*-->?msU', '', $text);
}

/**
 * Returns the language links within a text as a array [language_key] => article_name
 */
function get_language_links ( &$text , $use_global = true ) {
	global $language_links , $language_codes ;
	$ret = array () ;
	$a = explode ( "[[" , " " . $text ) ;
	array_shift ( $a ) ;
	foreach ( $a AS $b ) {
		$c = explode ( ":" , $b , 2 ) ;
		if ( count ( $c ) != 2 ) continue ;
		$lang = trim ( strtolower ( array_shift ( $c ) ) ) ;
		if ( !in_array ( $lang , $language_codes ) ) continue ;
		$c = explode ( "]]" , array_shift ( $c ) , 2 ) ;
		if ( count ( $c ) != 2 ) continue ;
		$c = array_shift ( $c ) ;
		$ret[$lang] = $c ;
		if ( $use_global ) $language_links[$lang] = $c ;
	}
	return $ret ;
}

function scan_interwiki_pages ( &$texts , &$language_links , $lang , $title , $initial = false , $do_output = true , $did_write = false ) {
	$lang = strtolower ( trim ( $lang ) ) ;
	if ( $lang == "" ) return ;
	if ( !$initial && isset ( $texts[$lang] ) ) return ; # Already done
	
	if ( !isset ( $texts[$lang] ) ) { # Can be skipped for $initial == true
		if ( $do_output ) {
			if ( !$did_write ) print "Loading " ;
			else print ", " ;
			$did_write = true ;
			$url = get_wikipedia_url ( $lang , $title ) ;
			print "<i><a href='{$url}'>{$lang}:" . wiki2html ( $title ) . "</a></i>" ;
			myflush () ;
		}
		$texts[$lang] = get_wikipedia_article ( $lang , $title ) ;
	}
	$lls = get_language_links ( $texts[$lang] , false ) ;
	
	if ( !isset ( $language_links[$lang] ) ) {
		$language_links[$lang] = array () ;
	}
	
	# Recursively scan other languages
	foreach ( $lls AS $llk => $llv ) {
		$llk = strtolower ( trim ( $llk ) ) ;
		if ( $llk == "" ) continue ;
		$language_links[$lang][$llk] = $llv ;
		scan_interwiki_pages ( $texts , $language_links , $llk , $llv , false , $do_output , $did_write ) ;
	}
}

function get_articles_in_languages ( &$language_links ) {
	$ret = array () ;
	foreach ( $language_links AS $lang_from => $targets ) {
		$ret = array_merge ( $ret , $targets ) ;
	}
	return $ret ;
}

function get_missing_language_links ( $lang , &$ail , &$language_links ) {
	$ret = array () ;
	foreach ( $ail AS $l => $t ) {
		if ( $lang == $l ) continue ;
		if ( isset ( $language_links[$lang][$l] ) ) continue ;
		$ret[$l] = $t ;
	}
	return $ret ;
}


/**
 * Returns the URL for a language/title combination
 * May be called with additional parameter $action
 */
function get_wikipedia_url ( $lang , $title , $action = "" , $project = "wikipedia" ) {
	$lang = trim ( strtolower ( $lang ) ) ;
	$url = "http://" ;
	if ( $lang != 'xxx' and $project != 'wikisource' ) $url .= "{$lang}." ;
	if ( $lang == "commons" ) $url .= "wikimedia" ;
	else $url .= $project ;
	$url .= ".org/w/index.php?" ;
	if ( $action != "" ) $url .= "action={$action}&" ;
	$url .= "title=" . myurlencode ( $title ) ;
	return $url ;
}

function get_article_from_database ( $lang , $title ) {
	global $mysql_con , $mysql_password ;
	
	$lang = trim ( strtolower ( $lang ) ) ; # Paranoia
	$title = ucfirst ( str_replace ( ' ' , '_' , $title ) ) ;
	
	if ( !isset ( $mysql_con ) ) {
		if ( 0 ) { # Testing
			$server = "127.0.0.1" ;
			$user = "wikiuser" ;
			$db = "wikidb" ;
			$password = "wikiuser" ;
		} else { # Production
			$server = "sql" ;
			$user = "magnus" ;
			$db = "{$lang}wiki_p" ;
			$password = $mysql_password ;
		}

		if ( !$mysql_con = mysql_connect ( $server , $user , $password ) ) {
			echo 'Could not connect to mysql';
			exit;
		}
	}
	
	print "Attempting to get data from page<br/>" ;
	$sql = "SELECT ".get_tool_name()."".get_tool_name()." * FROM page WHERE page_namespace='0' AND page_title='{$title}'" ;
	$res = mysql_db_query ( $db , $sql , $mysql_con ) ;
	if ( !$res ) {
		echo "Error when trying to contact {$db} (page)" ;
		exit ;
	}
	$o = mysql_fetch_object ( $res ) ;
	print_r ( $o ) . "<br/>" ;
	$page_id = $o->page_id ;
	$rev_id = $o->page_latest ;
	
	print "Attempting to get data from revision<br/>" ;
	$sql = "SELECT ".get_tool_name()." * FROM revision WHERE rev_id='{$rev_id}' AND rev_page='{$page_id}'" ;
	$res = mysql_db_query ( $db , $sql , $mysql_con ) ;
	if ( !$res ) {
		echo "Error when trying to contact {$db} (revision)" ;
		exit ;
	}
	$o = mysql_fetch_object ( $res ) ;
	print_r ( $o ) . "<br/>" ;
	$text_id = $o->rev_text_id ;

	print "Attempting to get data from text<br/>" ;
	$sql = "SELECT ".get_tool_name()." * FROM text WHERE old_id='{$text_id}'" ;
	$res = mysql_db_query ( $db , $sql , $mysql_con ) ;
	if ( !$res ) {
		echo "Error when trying to contact {$db} (text)" ;
		exit ;
	}
	$o = mysql_fetch_object ( $res ) ;
	print_r ( $o ) . "<br/>" ;

	$text = getRevisionText ( $o ) ;
#	$text = $o->old_text ;
#	if ( false !== strpos ( $old_flags , "gzip" ) ) $text = gunzip ( $text ) ;

	
	return $text ;
}

/**
 * Returns the raw text of a wikipedia page, trimmed and with html comments removed
 * Returns empty string if something went wrong
 */
function get_wikipedia_article ( $lang , $title , $allow_redirect = true , $project = "wikipedia" ) {
	global $is_on_toolserver ;
	if ( $is_on_toolserver ) {
		$u = myurlencode ( $title ) ;
		$url = "http://tools.wikimedia.de/~daniel/WikiSense/WikiProxy.php?wiki={$lang}.{$project}.org&title={$u}&rev=0&go=Fetch" ;
#		$text = get_article_from_database ( $lang , $title ) ;
	} else {
		$url = get_wikipedia_url ( $lang , $title , "raw" , $project ) ;
	}
	$max_attempts = 2 ;
	$cnt = 0 ;
	do {
		$text = @file_get_contents ( $url ) ;
		$cnt++ ;
		if ( $cnt > 1 ) $url = get_wikipedia_url ( $lang , $title , "raw" , $project ) ; # On toolserver, try alternate URL
	} while ( $text === false && $cnt < $max_attempts ) ;
	if ( $text === false ) {
		# Wikipedia did not return anything
		$text = "" ;
	}
	if ( substr ( $text , 0 , 10 ) == '<!DOCTYPE ' ) {
		# Wikipedia did not return raw text
		$text = "" ;
	}

	$text = trim ( strip_html_comments ( $text ) ) ;
	
	# REDIRECT?
	if ( $allow_redirect && strtoupper ( substr ( $text , 0 , 9 ) ) == "#REDIRECT" ) {
		$text = substr ( $text , 9 ) ;
		$text = array_shift ( explode ( "\n" , $text , 2 ) ) ;
		$text = str_replace ( "[[" , "" , $text ) ;
		$text = str_replace ( "]]" , "" , $text ) ;
		$text = ucfirst ( trim ( $text ) ) ;
#		print "Redirected to {$text}<br/>" ;
		return get_wikipedia_article ( $lang , $text , false ) ;
	}
	return $text ;
}

/**
 * Uses CommonSense to get categories for an image
 */
function common_sense ( $lang , $image , $keywords = array () ) {
	$ret = real_common_sense ( $lang , $image , $keywords , array ( 'CATEGORIES' ) , true ) ;
	if ( !isset ( $ret['CATEGORIES'] ) ) return array() ;
	return $ret['CATEGORIES'] ;
}

function real_common_sense ( $lang , $image , $keywords , $sections , $force_move = false ) {
	global $forbidden_commonsense_categories ;
	$kw = array () ;
	foreach ( $keywords AS $k ) $kw[] = urlencode ( $k ) ;
	$kw = implode ( '%0D%0A' , $kw ) ;
	
	$lang2 = $lang ;
	$go = 'clean' ;
	if ( $lang != 'commons' and $force_move ) {
		$lang2 .= '.wikipedia' ;
		$go = 'move' ;
	}
	
	$url = 'http://tools.wikimedia.de/~daniel/WikiSense/CommonSense.php?u=en&' .
		'i=' . myurlencode ( $image ) .
		'&kw=' . $kw .
		'&r=on' .
		'&p=_20' .
		'&cl=' .
		'&w=' .	$lang2 .
		'&go-' . $go . '=Find+Categories' . # was : go-move
		'&v=0' ;
#	print "TESTING : " . $lang . " " . $url . "<hr/>" ;
#	do {
		$text = @file_get_contents ( $url ) ;
#	} while ( $text === false ) ;
	$bot = explode ( "\n" , utf8_decode ( $text ) ) ;
	$group = "" ;
	$cats = array () ;
	foreach ( $bot AS $l ) {
		$l = ucfirst ( trim ( $l ) ) ;
		if ( substr ( $l , 0 , 1 ) == '#' ) { # Set new group
			$group = explode ( ' ' , substr ( $l , 1 ) ) ;
			$group = array_shift ( $group ) ;
			$did_this_category = array() ;
			continue ;
		}
		if ( !in_array ( $group , $sections ) ) continue ; # Only interested in categories
		if ( trim ( $l ) == "" ) continue ; # No blank category
#		print "TESTING : $group<br/>" ;
		
		$l2 = $group . '#' . $l ;
		if ( isset ( $did_this_category[$l2] ) ) continue ; # Each category only once
		$l = str_replace ( '_' , ' ' , $l ) ;
		if ( in_array ( trim ( strtolower ( $l ) ) , $forbidden_commonsense_categories ) ) continue ;
		$did_this_category[$l2] = 1 ;
		if ( !isset ( $cats[$group] ) ) $cats[$group] = array () ;
		$cats[$group][] = $l ;
	}
	return $cats ;
}


function get_initial_paragraph ( &$text , $language = '' ) {
	global $image_aliases ;
	$t = explode ( "\n" , $text ) ;
	while ( count ( $t ) > 0 ) {
		$s = trim ( array_shift ( $t ) ) ;
		if ( $s == "" ) continue ;
		if ( substr ( $s , 0 , 2 ) == '{{' ) { # Template
			if ( substr ( $s , -2 , 2 ) == '}}' ) continue ; # One-line template
			while ( count ( $t ) > 0 && substr ( $s , -2 , 2 ) != '}}' ) {
				$s = trim ( array_shift ( $t ) ) ;
			}
			continue ;
		}
		if ( substr ( $s , 0 , 2 ) == '--' ) continue ; # <hr>
		if ( substr ( $s , 0 , 1 ) == ':' ) continue ; # Remark
		if ( substr ( $s , 0 , 1 ) == '=' ) continue ; # Heading
		if ( substr ( $s , 0 , 1 ) == '<' ) continue ; # HTML
		if ( substr ( $s , 0 , 1 ) == '!' ) continue ; # Table fragment
		if ( substr ( $s , 0 , 1 ) == '|' ) continue ; # Table fragment
		if ( substr ( $s , 0 , 2 ) == '|-' ) continue ; # Table fragment
		if ( substr ( $s , 0 , 2 ) == '|}' ) continue ; # Table fragment
		if ( substr ( $s , 0 , 2 ) == '{|' ) { # Table
			while ( count ( $t ) > 0 && substr ( $s , 0 , 2 ) != '|}' ) {
				$s = trim ( array_shift ( $t ) ) ;
			}
			continue ;
		}
		
		$sl = strtolower ( $s ) ;
		
		# Check for images
		foreach ( $image_aliases AS $ia )
			{
			if ( false === strpos ( $sl , '[['.$ia ) ) continue ; # Image
			$sl = '' ;
			break ;
			}
		if ( $sl == '' ) continue ;
		
		if ( false !== strpos ( $sl , "|thumb|" ) ) continue ; # Image
		if ( false !== strpos ( $sl , "|frame|" ) ) continue ; # Image
		if ( false !== strpos ( $sl , "|right|" ) ) continue ; # Image

		if ( $language == 'eo' AND false !== strpos ( $sl , ">>" ) ) continue ; # Esperanto navigation line
		
		# Seems to be a real paragraph
		break ;
	}
	if ( count ( $t ) == 0 ) return "" ;
	return $s ;
}

function get_catscan_pages ( $lang , $category , $depth = 3 , $project = 'wikipedia' ) {
	$url = "http://tools.wikimedia.de/~daniel/WikiSense/CategoryIntersect.php?wikilang=" .
			$lang . "&wikifam=.{$project}.org&basecat=" .
			myurlencode ( $category ) . "&basedeep=" .
			$depth . "&templates=&mode=al&go=Scan&raw=on&userlang=en" ;
	$text = @file_get_contents ( $url ) ;
	#print "<br/>{$url}<br/><pre>{$text}</pre><br/>" ;
	
	$ret = array () ;
	$lines = explode ( "\n" , $text ) ;
	foreach ( $lines AS $line ) {
		if ( trim ( $line ) == "" ) continue ;
		$l = explode ( "\t" , $line ) ;
		$ns = array_shift ( $l ) ;
		$title = array_shift ( $l ) ;
		if ( count ( $l ) > 0 ) $categories = array_shift ( $l ) ;
		else $categories = "" ;
		$o = "" ;
		$o->namespace = $ns ;
		$o->title = str_replace ( "_" , " " , $title ) ;
		$o->categories = explode ( "|" , $categories ) ;
		$ret[] = $o ;
	}
	return $ret ;
}


function get_catscan_pages2 ( $language , $category , $depth = 3 , $project = 'wikipedia' , $initial = true ) {
	global $mysql_con , $mysql_password ;
	$ret = array () ;
	if ( $initial ) {
		$language = mysql_escape_string ( $language ) ;
		$project = mysql_escape_string ( $project ) ;
		$category = mysql_escape_string ( str_replace ( ' ' , '_' , $category ) ) ;
	}

	if ( $mysql_password == "" && !get_database_password() ) {
		print "Sorry, no database connection available" ;
		exit ;
	}

	$server = "sql" ;
	$user = "magnus" ;
	$db = "{$language}wiki_p" ;
	$password = $mysql_password ;

	if ( !isset ( $mysql_con ) ) {
		if ( !$mysql_con = mysql_connect ( $server , $user , $password ) ) {
			echo 'Could not connect to mysql';
			exit;
		}
	}
	
#	print "Scanning {$category}<br/>" ; myflush () ;
	

	# Pages
	$sql = "SELECT ".get_tool_name()." page_id,page_title FROM page,categorylinks WHERE cl_to='{$category}' AND page_id=cl_from AND page_namespace=0" ;
	$res = mysql_db_query ( $db , $sql , $mysql_con ) ;
	while ( $o = mysql_fetch_object ( $res ) ) {
		if ( in_array ( $o->page_title , $ret ) ) continue ;
		$ret[] = $o->page_title ;
#		print "Page : {$o->page_title}<br/>" ; myflush () ;
	}
	
	# Subcategories
	if ( $depth > 0 ) {
		$sql = "SELECT ".get_tool_name()." page_id,page_title FROM page,categorylinks WHERE cl_to='{$category}' AND page_id=cl_from AND page_namespace=14" ;
		$res = mysql_db_query ( $db , $sql , $mysql_con ) ;
		while ( $o = mysql_fetch_object ( $res ) ) {
			$pages = get_catscan_pages2 ( $language , $o->page_title , $depth - 1 , $project , false ) ;
			foreach ( $pages AS $page ) {
				if ( in_array ( $page , $ret ) ) continue ;
				$ret[] = $page ;
			}
		}
	}
	
	if ( $initial ) {
		$ret2 = array () ;
		foreach ( $ret AS $x ) {
			$o = "" ;
			$o->title = $x ;
			$ret2[] = $o ;
		}
		return $ret2 ;
	}
	
	return $ret ;
}

function query_categories ( $lang , $page , $project = 'wikipedia' ) {
	$url = "http://{$lang}.{$project}.org/w/query.php?format=php&what=categories&titles=" . myurlencode ( $page ) ;
	$data = unserialize ( file_get_contents ( $url ) ) ;
	
	$ret = array() ;
	$data = $data['pages'] ;
	$ak = array_shift ( array_keys ( $data ) ) ;
	if ( $ak < 0 ) return $ret ; # Nothing here
	$data = array_shift ( $data  ) ;
	if ( !isset ( $data['categories'] ) ) return $ret ; # No categories
	$data = $data['categories'] ;
	foreach ( $data AS $v ) {
		$ret[] = array_pop ( $v ) ;
	}
	return $ret ;
}


/**
 * Parses a text for image names
 * NOTE : This might return false positives
 */
function get_images ( $text ) {
	global $image_aliases ;
	$ret = array () ;
	while ( 1 ) {
		$text_lower = strtolower ( $text ) ;
		$pos = -1 ;
		foreach ( $image_aliases AS $x ) {
			$np = strpos ( $text_lower , $x ) ;
			if ( $np === false ) continue ;
			if ( $pos != -1 && $np > $pos ) continue ;
			$pos = $np ;
		}
		if ( $pos == -1 ) break ;
		
		$text = substr ( $text , $np ) ;
		$o = explode ( ':' , $text , 2 ) ;
		$text = array_pop ( $o ) ;
		
		$o = explode ( "\n" , $text , 2 ) ;
		$o = explode ( "|" , array_shift ( $o ) , 2 ) ;
		$o = trim ( array_shift ( $o ) ) ;
		if ( $o == "" ) continue ; # Not an image name
		$o2 = ucfirst ( $o ) ;
		if ( $o2 == 'Falta.png' ) continue ; # Reads "missing image" on es.wikipedia
		$ret[] = $o ;
	}
	return $ret ;
}

function get_image_url ( $lang , $image , $project = "wikipedia" ) {
	$image = utf8_encode ( $image ) ;
	$image2 = ucfirst ( str_replace ( " " , "_" , $image ) ) ;
	$m = md5( $image2 ) ;
	$m1 = substr ( $m , 0 , 1 ) ;
	$m2 = substr ( $m , 0 , 2 ) ;
	
	$url = "http://upload.wikimedia.org/{$project}/{$lang}/{$m1}/{$m2}/" . myurlencode ( $image ) ;
	return $url ;
}

function get_thumbnail_url ( $lang , $image , $width , $project = "wikipedia" ) {
	$image = $image ; #utf8_encode (  $image ) ;
	$image2 = ucfirst ( str_replace ( " " , "_" , $image ) ) ;
	$m = md5( $image2 ) ;
	$m1 = substr ( $m , 0 , 1 ) ;
	$m2 = substr ( $m , 0 , 2 ) ;
	
	$url = "http://upload.wikimedia.org/{$project}/{$lang}/thumb/{$m1}/{$m2}/" . myurlencode ( $image ) ;
	$url .= '/' . $width . 'px-' . myurlencode ( $image ) ;
	if ( strtolower ( substr ( $image , -4 , 4 ) ) == '.svg' ) $url .= '.png' ;
	return $url ;
}

function get_request ( $key , $default = "" ) {
	global $prefilled_requests ;
	if ( isset ( $prefilled_requests[$key] ) ) return $prefilled_requests[$key] ;
	if ( isset ( $_REQUEST[$key] ) ) return str_replace ( "\'" , "'" , $_REQUEST[$key] ) ;
	return $default ;
}

function get_common_header ( $target , $toolpage = '' ) {
	global $is_on_toolserver , $queryclass ;
	global $nameofthetool ;
	
	$ret = "" ;
	if ( $is_on_toolserver ) {
		$ret .= '<div style="float:right"><a href="http://tools.wikimedia.de"><img style="vertical-align:top" border=0 src="http://tools.wikimedia.de/images/wikimedia-toolserver-button.png" /></a></div>' ;
	}
	$ret .= "<span style='border:2px solid red;display:inline;float:left;padding:2px;font-size:150%;background-color:white'><a target='_blank' href='http://wikimediafoundation.org/wiki/Fundraising'>Donate to Wikimedia!</a></span>" ;
	$ret .= "<center style='width:100%; border-bottom:1px solid #AAAAAA;margin-bottom:3px;padding:2px;background-color:#AAFFAA'>" ;
	$ret .= "This is one of <a href='http://tools.wikimedia.de/~magnus/index.html'>Magnus' toys</a>. " ;
	$ret .= "Get the <a href='http://tools.wikimedia.de/~magnus/sources.php?script={$target}'>source of this script</a>" ;
	$ret .= ".<br/>&nbsp;" ;
	if ( $toolpage != '' ) {
		$ret .= "For more information, see <a href='http://meta.wikipedia.org/wiki/" . 
				myurlencode ( $toolpage ) . "'>{$toolpage}</a> on meta. " ;
	}
	$ret .= "<a href=\"https://jira.ts.wikimedia.org/browse/MAGNUS\">Bug reports and feature requests</a>" ;
	$ret .= "</center>" ;
#	$ret .= "<p><font color='red'><i>NOTE: Some of my tools are currently not working due to the broken toolserver databases.</i></font></p>\n" ; #!!!!!!
	return $ret ;
}

function myfileexists ( $url ) {
	$h = @fopen ( $url , "r" ) ;
	if ( $h === false ) return false ;
	fclose ( $h ) ;
	return true ;
}

function wiki2html ( $wiki ) {
	return htmlentities ( $wiki , ENT_NOQUOTES , "UTF-8" ) ;
}

function _get_browser()
{
  $browser = array ( //reversed array
   "OPERA",
   "MSIE",            // parent
   "NETSCAPE",
   "FIREFOX",
   "SAFARI",
   "KONQUEROR",
   "MOZILLA"        // parent
  );
 
  $info['browser'] = "OTHER";
  
  foreach ($browser as $parent) 
  {
   if ( ($s = strpos(strtoupper($_SERVER['HTTP_USER_AGENT']), $parent)) !== FALSE )
   {           
     $f = $s + strlen($parent);
     $version = substr($_SERVER['HTTP_USER_AGENT'], $f, 5);
     $version = preg_replace('/[^0-9,.]/','',$version);
              
     $info['browser'] = $parent;
     $info['version'] = $version;
     break; // first match wins
   }
  }
 
  return $info;
}

function get_images_of_user ( $lang , $project , $wikiuser ) {
	global $mysql_password ;
	if ( $mysql_password == "" && !get_database_password() ) {
		print "Sorry, no database connection available" ;
		exit ;
	}
	
	if ( $project == "wikipedia" ) $project = "wiki" ;
	
	
	$server = "sql" ;
	$user = "magnus" ;
	$db = "{$lang}{$project}_p" ;
	$password = $mysql_password ;

	if ( !$mysql_con = mysql_connect ( $server , $user , $password ) ) {
		echo 'Could not connect to mysql';
		exit;
	}
	
	$wikiuser = addslashes ( str_replace ( '_' , ' ' , $wikiuser ) ) ; # Paranoia
	$sql = "SELECT ".get_tool_name()." img_name FROM image WHERE img_user_text=\"{$wikiuser}\"" ;
	$res = mysql_db_query ( $db , $sql , $mysql_con ) ;
	if ( !$res ) {
		echo "Error when trying to contact {$db} (page)" ;
		exit ;
	}
	
	$ret = array () ;
	while ( $o = mysql_fetch_object ( $res ) ) $ret[] = $o->img_name ;

	return $ret ;
}

function xml_cut_between ( $xml , $begin , $end ) {
	$ret = array_pop ( explode ( $begin , $xml , 2 ) ) ;
	$ret = trim ( array_shift ( explode ( $end , $ret , 2 ) ) ) ;
	if ( $ret == $xml ) $ret = "" ;
	return $ret ;
}

function get_page_object ( $title , $project , $language = '' ) {
	if ( $project == 'commons' ) {
		$language = 'commons' ;
		$project = 'wikimedia' ;
	}
	$url = "http://{$language}.{$project}.org/wiki/Special:Export/" . myurlencode ( $title ) ;

	$max_attempts = 2 ;
	$cnt = 0 ;
	do {
		$text = @file_get_contents ( $url ) ;
		$cnt++ ;
	} while ( $text === false && $cnt < $max_attempts ) ;

	$o = "" ;
	$o->title = $title ;
	if ( $text === false || count ( explode ( '</text>' , $text ) ) < 2 ) {
		$o->xml = "" ;
		$o->text = "" ;
		$o->ok = false ;
	} else {
		$lastrev = array_pop ( explode ( '<revision>' , $text ) ) ;
		$o->xml = $text ;
		$o->text = xml_cut_between ( $lastrev , '<text xml:space="preserve">' , '</text>' ) ;
		$o->user = xml_cut_between ( $lastrev , '<username>' , '</username>' ) ;
		$ts = xml_cut_between ( $lastrev , '<timestamp>' , '</timestamp>' ) ;

		$t = str_replace ( '-' , '' , $ts ) ;
		$t = str_replace ( ':' , '' , $t ) ;
		$t = str_replace ( 'T' , '' , $t ) ;
		$o->clean_timestamp = str_replace ( 'Z' , '' , $t ) ;
		
		$date = explode ( '-' , $ts ) ;
		$time = explode ( ':' , $ts ) ;
		$o->year = array_shift ( $date ) ;
		$o->month = array_shift ( $date ) ;
		$o->day = substr ( array_shift ( $date ) , 0 , 2 ) ;
		$o->hour = substr ( array_shift ( $time ) , -2 , 2 ) ;
		$o->min = array_shift ( $time ) ;
		$o->sec = substr ( array_shift ( $time ) , 0 , 2 ) ;
		$o->timestamp = mktime ( $o->hour , $o->min , $o->sec , $o->month , $o->day , $o->year ) ;
		$o->age = time() - $o->timestamp ;
		$o->age_days = round ( $o->age / 3600 / 24 ) ;
		$o->ok = true ;
	}
	
	return $o ;
}

function mask_quotes ( $text ) {
	return str_replace ( "'" , htmlentities ( "'" , ENT_QUOTES ) , $text ) ;
}

function get_database_password () {
	global $mysql_password ;
	if ( file_exists ( "../.my.cnf" ) ) {
		$t = file_get_contents ( "../.my.cnf" ) ;
		$lines = explode ( "\n" , $t ) ;
		foreach ( $lines AS $l ) {
			$l = trim ( $l ) ;
			if ( substr ( $l , 0 , 8 ) != 'password' ) continue ;
			$l = explode ( '"' , $l ) ;
			array_shift ( $l ) ;
			$mysql_password = array_shift ( $l ) ;
		}
		return true ;
	} else return false ;
}

# API service keys

function get_service_key ( $service ) {
	global $service_keys ;
	if ( isset ( $service_keys[$service] ) ) return $service_keys[$service] ;
	if ( file_exists ( "../{$service}_key.txt" ) ) {
		$service_keys[$service] = trim ( file_get_contents ( "../{$service}_key.txt" ) ) ;
		return $service_keys[$service] ;
	}
	$service_keys[$service] = "" ; # BLANK, does not exist?
	return "" ;
}

function get_flickr_key () {
	return get_service_key ( "flickr" ) ;
}

function get_yahoo_key () {
	return get_service_key ( "yahoo" ) ;
}



# Main function, if called as primary script
$mysql_password = "" ;
if ( isset ( $_REQUEST['common_source'] ) ) {
	$title = $_REQUEST['common_source'] ;
	$title = str_replace ( '../' , '/' , $title ) ;
	$text = @file_get_contents ( "./" . $title ) ;
	header('Content-type: text/text; charset=utf-8');
	print $text ;
	exit ;
}

function image_dimensions ( $url , &$i_width , &$i_height , $i_max = 120 ) {
	list($i_width, $i_height, $i_type, $i_attr) = @getimagesize($url);
	if ( $i_width <= 0 ) { # Paranoia
		$i_width = $i_max ;
		$i_height = $i_max ;
	}
}

function get_random_title ( $lang , $project , $namespace = "" ) {
	$url = "http://{$lang}.{$project}.org/w/index.php?title=Special:Randompage" ;
	if ( $namespace != "" ) $url .= "/" . $namespace ;
	$text = @file_get_contents ( $url ) ;
	if ( $text === false ) return false ;
	$text = explode ( '<h1 class="firstHeading">' , $text , 2 ) ;
	$text = explode ( "</h1>" , array_pop ( $text ) , 2 ) ;
	$title = trim ( array_shift ( $text ) ) ;
	if ( $title == '' ) return false ;
	return $title ;
}

function get_images_from ( $lang , $project , $startfrom ) {
	$url = get_wikipedia_url ( $lang , "Special:Allpages" , "" , $project ) . "&from={$startfrom}&namespace=6" ;
	do {
		$text = @file_get_contents ( $url ) ;
		if ( $text == "" ) sleep ( 1 ) ;
	} while ( $text == "" ) ;
	$text = array_pop ( explode ( '<table' , $text ) ) ;
	$links = explode ( '<a ' , $text ) ;
	array_shift ( $links ) ; # Remove dummy part
	foreach ( $links AS $link ) {
		$link = array_pop ( explode ( '>' , $link , 2 ) ) ;
		$link = array_shift ( explode ( '</a>' , $link , 2 ) ) ;
		$ret[] = $link ;
	}
	return $ret ;
}


# Interface localization
function load_interface_localization_sub ( $language , $lines , &$ret ) {
	global $helplink , $helptext ;
	$curlang = '' ;
	$key = '' ;
	foreach ( $lines AS $l ) {
		if ( substr ( $l , 0 , 2 ) == '==' ) { # Language section
			$curlang = strtolower ( trim ( str_replace ( '=' , '' , $l ) ) ) ;
			$key = '' ;
			continue ;
		}
		if ( substr ( $l , 0 , 2 ) == '|}' ) {
			$curlang = '' ;
			$key = '' ;
			continue ;
		}
		if ( substr ( $l , 0 , 1 ) == '!' ) { # Key?
			$key = trim ( substr ( $l , 1 ) ) ;
			if ( $language == $curlang ) $ret[$key] = '' ;
			continue ;
		}
		if ( $key == '' ) continue ;
		if ( substr ( $l , 0 , 1 ) == '|' AND substr ( $l , 0 , 2 ) != '|-' ) { # Value?
			$value = trim ( substr ( $l , 1 ) ) ;
			if ( $key == 'helptext' ) $helptext[$curlang] = $value ;
			if ( $key == 'helplink' ) $helplink[$curlang] = $value ;
			if ( $language != $curlang ) continue ;
			$ret[$key] .= $value ;
		}
	}
}

function load_interface_localization ( $url , $language ) {
	$ret = array () ;
#	do {
		$text = @file_get_contents ( $url ) ;
#	} while ( $text === false ) ;
	$lines = explode ( "\n" , $text ) ;
	$language = strtolower ( trim ( $language ) ) ;
	load_interface_localization_sub ( 'en' , $lines , $ret ) ;
	if ( $language != 'en' ) load_interface_localization_sub ( $language , $lines , $ret ) ;
	return $ret ;
}

function CheckUsageToo ( $title , $language , $project ) {
	$ret = array() ;
	$url = "http://{$language}.{$project}.org/w/query.php?format=xml&what=imagelinks&titles=" . myurlencode ( $title ) ;
	#print "|{$url}|" ;
	
	$xml = @file_get_contents ( $url ) ;
	if ( $xml == "" ) return $ret ;
	
	$il = xml_cut_between ( $xml , '<imagelinks>' , '</imagelinks>' ) ;
	$il = explode ( '</il>' , $il ) ;
	foreach ( $il AS $i ) {
		$i = trim ( array_pop ( explode ( '>' , $i , 2 ) ) ) ;
		if ( $i == '' ) continue ;
		$ret[] = $i ;
	}
	return $ret ;
}

function get_random_title_from_db ( $language , $project , $ns = 0 ) {
	$data = db_get_random_title ( $language , $project , $ns , 1 ) ;
	return array_pop ( $data ) ;
}

function get_edit_timestamp ( $lang , $project , $title ) {
	$t = "http://{$lang}.{$project}.org/wiki/Special:Export/" . myurlencode ( $title ) ;
	$t = @file_get_contents ( $t ) ;
#	$desc = $t ;
	$t = explode ( '<timestamp>' , $t , 2 ) ;
	$t = explode ( '</timestamp>' , array_pop ( $t ) , 2 ) ;
	$t = array_shift ( $t ) ;
	$t = str_replace ( '-' , '' , $t ) ;
	$t = str_replace ( ':' , '' , $t ) ;
	$t = str_replace ( 'T' , '' , $t ) ;
	$t = str_replace ( 'Z' , '' , $t ) ;
	return $t ;
}

function cGetEditButton ( $text , $title , $lang , $project , $summary , $button_label , $new_window = true , $add = false , $diff = false , $minor = false ) {
	global $toynote ;
	if ( !isset ( $toynote ) ) $toynote = '' ;
	
	$t = get_edit_timestamp ( $lang , $project , $title ) ;
	$timestamp = $t ;
	
	$text = str_replace ( "'" , htmlentities ( "'" , ENT_QUOTES ) , $text ) ;
	$summary = str_replace ( "'" , htmlentities ( "'" , ENT_QUOTES ) , $summary.$toynote ) ;

	$url = "http://{$lang}.{$project}.org/w/index.php?title=" . myurlencode ( $title ) . '&action=edit' ;
	if ( $add ) $url .= '&section=new' ;
	$ncb = "<form id='upload' method=post enctype='multipart/form-data'" ;
	if ( $new_window ) $ncb .= " target='_blank'" ;
	$ncb .= " action='{$url}' style='display:inline'>" ;
	$ncb .= "<input type='hidden' name='wpTextbox1' value='{$text}'/>" ;
	$ncb .= "<input type='hidden' name='wpSummary' value='{$summary}'/>" ;
	if ( $diff ) $ncb .= "<input type='hidden' name='wpDiff' value='wpDiff' />" ;
	else $ncb .= "<input type='hidden' name='wpPreview' value='wpPreview' />" ;
	
	$starttime = date ( "YmdHis" , time() + (12 * 60 * 60) ) ;
	$ncb .= "<input type='hidden' value='{$starttime}' name='wpStarttime' />" ;
	$ncb .= "<input type='hidden' value='{$t}' name='wpEdittime' />" ;

  if ( $minor ) $ncb .= "<input type='hidden' value='1' name='wpMinoredit' />" ;
	if ( $diff ) $ncb .= "<input type='submit' name='wpDiff' value='$button_label'/>" ;
	else $ncb .= "<input type='submit' name='wpPreview' value='$button_label'/>" ;
	$ncb .= "</form>" ;
	return $ncb ;
}


function fix_language_code ( $lang , $default = "en" ) {
  $lang = trim ( strtolower ( $lang ) ) ;
  if ( preg_match ( "/^([\-a-z]+)/" , $lang , $l ) ) {
    $lang = $l[0] ;
  } else $lang = $default ; // Fallback
  return $lang ;
}

function check_project_name ( $p ) {
  $p = trim ( strtolower ( $p ) ) ;
  if ( $p == 'wikipedia' ) return $p ;
  if ( $p == 'wikimedia' ) return $p ;
  if ( $p == 'wikibooks' ) return $p ;
  if ( $p == 'wikisource' ) return $p ;
  if ( $p == 'wikinews' ) return $p ;
  if ( $p == 'wikispecies' ) return $p ;
  print "WRONG PROJECT : $p!" ;
  exit ; # 
}


# MAIN CODE

@set_time_limit ( 5*60 ) ; # Time limit 5min
ini_set('user_agent','MSIE 4\.0b2;'); # Fake user agent

if ( !isset ( $hide_header ) ) {
	header('Content-type: text/html; charset=utf-8');
}
if ( !isset ( $hide_doctype ) ) {
	print '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">' . "\n\n" ;
}

?>