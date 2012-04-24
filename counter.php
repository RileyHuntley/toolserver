<?php
$counter = intval(file_get_contents("counter.txt")) + 1;
$fp = fopen("counter.txt", "w");
fputs($fp, "$counter");
fclose($fp);
echo $counter;
?>
