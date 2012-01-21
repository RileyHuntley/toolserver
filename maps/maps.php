<?php

# Copyright (C) 2012 kolossos, emijrp
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

$fa=25; #size
$centerx=-7; # longitude center
$centery=36; # latitude center
$width=25; #max width in degrees
$height=20; #max height degress
// connection to database 
require("../../database.inc");
mysql_connect('sql-s4',$toolserver_username,$toolserver_password);
@mysql_select_db('u_dispenser_p') or print mysql_error();
$im = @ImageCreate ($width*$fa, $height*$fa) or die ("Kann keinen neuen GD-Bild-Stream erzeugen");
$background_color = ImageColorAllocate ($im, 0, 0, 0);
for($i = 0; $i <= 255; $i++) {$t_color = ImageColorAllocate ($im,$i , $i, $i);}
 $sql="SELECT ROUND($fa*`gc_lat`,0)/$fa ,ROUND($fa*`gc_lon`,0)/$fa,COUNT(*)  FROM `coord_commonswiki`  GROUP BY ROUND($fa*`gc_lat`,0)/$fa,ROUND($fa*`gc_lon`,0)/$fa HAVING COUNT(*)>0";
 $qres = mysql_query($sql);
while($res = mysql_fetch_array($qres)) 
{ 
    if ($res[2]>0 && $res[0]>=$centery-($height/2) && $res[0]<=$centery+($height/2) && $res[1]>=$centerx-($width/2) && $res[1]<=$centerx+($width/2)){
         $colo=380*log10(1+log10($res[2]+10)+0.2);
         imagesetpixel ($im,$fa*($width/2-$centerx)+$fa*$res[1],$fa*($height/2+$centery)-$fa*$res[0],imagecolorclosest($im,$colo,$colo,$colo));
         //echo $res[0]." ".$res[1]." ".$res[2]."\n";
         //echo ($fa*180+$fa*$res[1])." ".($fa*90-$fa*$res[0])."\n";
    }
}

//header ("Content-type: image/png");
imagepng ($im, 'a.png');
imagedestroy ($im);
?>
