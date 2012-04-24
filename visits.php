<?php
$counter = intval(file_get_contents("visits.txt")) + 1;
$fp = fopen("visits.txt", "w");
fputs($fp, "$counter");
fclose($fp);
echo $counter;
?>
