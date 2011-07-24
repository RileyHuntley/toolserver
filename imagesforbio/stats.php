<?
require_once('../../database.inc');
mysql_connect('sql',$toolserver_username,$toolserver_password);
@mysql_select_db('u_emijrp_yarrow') or print mysql_error();

echo '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"><html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en" dir="ltr"><head><meta http-equiv="Content-Type" content="text/html; charset=utf-8" /><link rel="stylesheet" href="style.css" type="text/css" /></head><body>';

echo "<center><table style='text-align:center;'><tr><td><img src='im1.jpg'></td><td><h1><a href='http://toolserver.org/~emijrp/imagesforbio/'>Images for biographies</a></h1></td><td><img src='im2.png'></td></tr></table></center><br/><center>Some statistics for this amazing tool. Thanks to all users who added any image.</center><br/><center><table id='langs' border=1px style='text-align: center;'><tr><th>Language</th><th>To do</th><th>Done</th><th>Total</th><th>Done (%)</th></tr>";

$langs=array();
$query="select language from imagesforbios group by language";
$result = mysql_query($query);
if(!$result) Die("ERROR: No result returned.");
while($row = mysql_fetch_assoc($result))
{
	array_push($langs, $row['language']);
}

$totaldone=0;
$totaltodo=0;
foreach($langs as $lang)
{
	$query="select count(*) from imagesforbios where done=0 and language='{$lang}' group by article";
       $result = mysql_query($query);
       if(!$result) Die("ERROR: No result returned.");
       $todo=0;
       while($row = mysql_fetch_assoc($result))
       {
	      $todo+=1;
       }

       $query="select count(*) from imagesforbios where done=1 and language='{$lang}' group by article";
       $result = mysql_query($query);
       if(!$result) Die("ERROR: No result returned.");
       $done=0;
       while($row = mysql_fetch_assoc($result))
       {
	      $done+=1;
       }
    $percent = number_format($done/(($todo+$done)/100), 2);
    $color = 'pink';
    if ($percent < 25) {
        $color = 'pink';
    }else if ($percent < 50) {
        $color = 'orange';
    }else if ($percent < 75) {
        $color = 'yellow';
    }else if ($percent < 100) {
        $color = 'lightgreen';
    }else if ($percent == 100) {
        $color = 'lightblue';
    }
	echo "<tr><td><a href=index.php?language={$lang}&show=0>{$lang}</a></td><td>{$todo}</td><td>{$done}</td><td>".($todo+$done)."</td><td bgcolor=${color}>".$percent."%</td></tr>";
       $totaltodo+=$todo;
       $totaldone+=$done;
}

echo "<tr><td>All</td><td>{$totaltodo}</td><td>{$totaldone}</td><td>".($totaldone+$totaltodo)."</td><td>".number_format($totaldone/(($totaldone+$totaltodo)/100), 2)."%</td></tr>";
echo "</table><br/>This tool has been reset several times. Total images added to articles since 2010: XXXX.</center>";

?>
