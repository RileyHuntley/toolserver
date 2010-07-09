<?
require_once('../../database.inc');
mysql_connect('sql',$toolserver_username,$toolserver_password);
@mysql_select_db('u_emijrp_yarrow') or print mysql_error();

echo '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"><html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en" dir="ltr"><head><meta http-equiv="Content-Type" content="text/html; charset=utf-8" /><link rel="stylesheet" href="style.css" type="text/css" /></head><body>';

$done=0;
if (isset($_POST['done']))
{
	$done=$_POST['done'];
	$done=intval($done);
	$query="";
	$query="update imagesforbio set done=not done where id={$done}";
	$result = mysql_query($query);
	if(!$result) Die("ERROR: No result returned.");
}

$langs=array();
$query="select language from imagesforbio group by language";
$result = mysql_query($query);
if(!$result) Die("ERROR: No result returned.");
while($row = mysql_fetch_assoc($result))
{
	array_push($langs, $row['language']);
}

$language="all";
if (isset($_GET['language']))
{
	$temp=$_GET['language'];
	if (in_array($temp, $langs))
		$language=$temp;
}else if(isset($_POST['lang']))
{
	$temp=$_POST['lang'];
	if (in_array($temp, $langs))
		$language=$temp;
}

$show=0;
if ($_GET['show'])
{
	$show=$_GET['show'];
	$show=intval($show);
}

#contador
/*$c1=0;
$c2=0;
$query="select count(*) from imagesforbio where done=1";
$result = mysql_query($query);
if(!$result) Die("ERROR: No result returned.");
while($row = mysql_fetch_assoc($result))
{
	$c1=$row['count(*)'];
}
$query="select count(*) from imagesforbio where done=0";
$result = mysql_query($query);
if(!$result) Die("ERROR: No result returned.");
while($row = mysql_fetch_assoc($result))
{
	$c2=$row['count(*)'];
}*/

//echo "<center><table style='text-align:center;'><tr><td><img src='im1.jpg'></td><td><h1><a href='http://toolserver.org/~emijrp/imagesforbio/'>Images for biographies</a><sup><span style='font-color:#ff0000;'>new!</span></sup></h1></td><td><img src='im2.png'></td></tr><tr><td colspan=3><b>{$c1} done or useless, {$c2} left (".number_format($c1/($c1+$c2/100),2)."% completed)</b></td></tr></table></center>This tool is being tested. If you get problems by putting images on your Wikipedia, or odd characters like this ??? ?????? ??, please <a href='http://en.wikipedia.org/wiki/User_talk:Emijrp'>tell me</a> and show me a diff. Also, you can help <a href='http://en.wikipedia.org/wiki/User:BOTijo/Images_for_biographies'>translating this tool</a>.<hr/><center><b>Select language:</b> <a href=index.php?language=all>All</a> ({$c2})";
echo "<center><table style='text-align:center;'><tr><td><img src='im1.jpg'></td><td><h1><a href='http://toolserver.org/~emijrp/imagesforbio/'>Images for biographies</a><sup><span style='font-color:#ff0000;'>new!</span></sup></h1></td><td><img src='im2.png'></td></tr></table></center><center><b>PLEASE! Check images before insert them. Do not insert images not related with the article subject. Thanks.</b><br/>You can help <a href='http://en.wikipedia.org/wiki/User:BOTijo/Images_for_biographies'>translating this tool</a> and reporting <a href='http://en.wikipedia.org/wiki/User_talk:Emijrp/Images_for_biographies/Exclusions'>wrong image&lt;---&gt;article</a> relations.<br/>How to use this tool? 1) Choose an image. 2) Press \"Add image to page\" (if the image is correct). 3) The Wikipedia article is loaded in a new tab. 4) If the article has an infobox template, move the image into the infobox. 5) Save changes pressing the save button. 6) Click \"Mark as done\" button to remove the image from this list.</center><hr/><center><b>Select language:</b> <a href=index.php?language=all>All</a>";

foreach($langs as $lang)
{
	echo " &ndash; <a href=index.php?language={$lang}&show={$show}>{$lang}</a>";
}
echo "<hr/>";

if ($show)
	echo "<b>Options:</b> <a href=index.php?language={$language}&show=0>Hide added or useless images</a> &ndash; <a href='stats.php'>Statistics</a>";
else
	echo "<b>Options:</b> <a href=index.php?language={$language}&show=1>Show added or useless images</a> &ndash; <a href='stats.php'>Statistics</a>";
echo "<hr/>";

$limit=15;
if ($language)
{
	if ($language=="all")
	{
		if ($show)
			$query = "select * from imagesforbio LIMIT order by article $limit";
		else
			$query = "select * from imagesforbio where done=0 order by article LIMIT $limit";
	}else{
		if ($show)
			$query = "select * from imagesforbio where language='{$language}' order by article LIMIT $limit";
		else
			$query = "select * from imagesforbio where language='{$language}' and done=0 order by article LIMIT $limit";
	}
	$result = mysql_query($query);
	if(!$result) Die("ERROR: No result returned.");

	echo "<center><table border=0 cellpadding=2><tr style='text-align: center;'><td><b>#</b></td><td><b>Language</b></td><td><b>Article</b></td><td><b>Image</b></td><td><b>Thumbnail</b></td><td><b>Action</b></td></tr>\n";
	$cont=0;
	while($row = mysql_fetch_assoc($result))
	{
		$id=$row['id'];
		$l=$row['language'];
		$a=$row['article'];
		$aa=str_replace(" ", "+", $a);
		$i=$row['image'];
		$ii=str_replace(" ", "+", $i);
		$u=$row['url'];
		$trozos=explode("http://upload.wikimedia.org/wikipedia/commons/", $u);
		$thumb="http://upload.wikimedia.org/wikipedia/commons/thumb/{$trozos[1]}/80px-{$i}";
		$d=$row['done'];
		
		if ($d)
		{
			if ($show)
			{
				$cont++;
				echo "<tr valign=middle style='text-align: center;background-color:#FFC0CB;'><td>{$cont}</td><td><a href='http://{$l}.wikipedia.org'>{$l}</a></td><td><a href=\"http://{$l}.wikipedia.org/wiki/{$a}\">{$a}</a></td><td><a href='http://commons.wikimedia.org/wiki/Image:{$i}'>{$i}</a></td><td><a href='http://commons.wikimedia.org/wiki/Image:{$i}'><img src='{$thumb}'></a></td><td><form method='post' action='index.php?language={$l}&show=1'><input type='hidden' name='done' value='{$id}'><input type='submit' value='Mark as undone'></form></td></tr>\n";
			}
		}else{ //#cedff2;
			$cont++;
			echo "<tr id='{$cont}' valign=middle style='text-align: center;background-color:#cedff2;'><td>{$cont}</td><td><a href='http://{$l}.wikipedia.org'>{$l}</a></td><td><a href=\"http://{$l}.wikipedia.org/wiki/{$a}\">{$a}</a></td><td><a href='http://commons.wikimedia.org/wiki/Image:{$i}'>{$i}</a></td><td><a href='http://commons.wikimedia.org/wiki/Image:{$i}'><img src='{$thumb}'></a></td><td><br/><form method='post' action='ilu.php' target='_blank'><input type='hidden' name='article' value='{$aa}'><input type='hidden' name='image' value='{$ii}'><input type='hidden' name='lang' value='{$l}'><input type='submit' value='Add image to page'></form><br/><form method='post' action='index.php'><input type='hidden' name='lang' value='{$l}'><input type='hidden' name='done' value='{$id}'><input type='submit' value='Mark as done'></form><br/><a href='http://en.wikipedia.org/wiki/User_talk:Emijrp/Images_for_biographies/Exclusions' target='_blank'>Report wrong image</a></td></tr>\n";
		}
	}
	echo "</table></center>\n";
}
 
mysql_close();

echo "<hr/><center>This is a tool of <a href='http://tools.wikimedia.de/~emijrp/'>WikiFORJA</a>. Developed by <a href='http://en.wikipedia.org/wiki/User:Emijrp'>emijrp</a> (some functions by <a href='http://tools.wikimedia.de/~magnus/'>magnus</a>)<br/><a href='http://tools.wikimedia.de/'><img src='wikimedia-toolserver-button.png'></a></center>";
echo "</body></html>";
?>
