<?php
$inputFile = "https://l2.metodbox.com/medya/24/247/2__fikrim_patentlenebilir_mi_nasil_patent_basvurusu_yapabilirim_1728651162.mp4?st=cvzE47G9axFgGJLZuBtFZw&e=1758173337";
$escaped = escapeshellarg($inputFile);
var_dump($escaped);
$command = escapeshellcmd('python -W ignore detect_speech.py "' . $inputFile . '"');
$output = [];
$return_var = 0;
exec($command, $output, $return_var);

if ($return_var === 0) {
    echo "Speech detected\n";
} else {
    echo "No speech\n";
}
?>
