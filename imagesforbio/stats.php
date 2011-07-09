<?
require_once('../../database.inc');
mysql_connect('sql',$toolserver_username,$toolserver_password);
@mysql_select_db('u_emijrp_yarrow') or print mysql_error();

echo '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"><html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en" dir="ltr"><head><meta http-equiv="Content-Type" content="text/html; charset=utf-8" /><link rel="stylesheet" href="style.css" type="text/css" /></head><body>';

echo "<center><table style='text-align:center;'><tr><td><img src='im1.jpg'></td><td><h1><a href='http://toolserver.org/~emijrp/imagesforbio/'>Images for biographies</a></h1></td><td><img src='im2.png'></td></tr></table></center><br/><center>Some statistics for this amazing tool. Thanks to all users who added any image.</center><br/><center><table id='langs' border=1px style='text-align: center;'><tr><th>Language</th><th>To do</th><th>Done</th><th>Total</th><th>Done (%)</th></tr>";

$langs=array();
$query="select language from imagesforbio group by language";
$result = mysql_query($query);
if(!$result) Die("ERROR: No result returned.");
while($row = mysql_fetch_assoc($result))
{
	array_push($langs, $row['language']);
}

$c1=0;
$c2=0;
foreach($langs as $lang)
{
	$query="select count(*) from imagesforbio where done=0 and language='{$lang}' group by article";
       $result = mysql_query($query);
       if(!$result) Die("ERROR: No result returned.");
       $c3=0;
       while($row = mysql_fetch_assoc($result))
       {
	      $c3+=1;
       }

       $query="select count(*) from imagesforbio where done=1 and language='{$lang}' group by article";
       $result = mysql_query($query);
       if(!$result) Die("ERROR: No result returned.");
       $c4=0;
       while($row = mysql_fetch_assoc($result))
       {
	      $c4+=1;
       }
	echo "<tr><td><a href=index.php?language={$lang}&show=0>{$lang}</a></td><td>{$c3}</td><td>{$c4}</td><td>".($c3+$c4)."</td><td>".number_format($c4/(($c3+$c4)/100), 2)."%</td></tr>";
       $c2+=$c3;
       $c1+=$c4;
}

echo "<tr><td>All</td><td>{$c2}</td><td>{$c1}</td><td>".($c1+$c2)."</td><td>".number_format($c1/(($c1+$c2)/100), 2)."%</td></tr>";
echo "</table><br/>This tool has been reset several times. Total images added to articles since 20: XXXX.</center>";

?>
