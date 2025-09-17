<?php
$python = '/Users/bkmobil/Projects/detect_video_speech/.venv/bin/python';
$script = __DIR__ . '/detect_speech.py';
$inputFile = 'https://l2.metodbox.com/medya/24/247/2__fikrim_patentlenebilir_mi_nasil_patent_basvurusu_yapabilirim_1728651162.mp4?st=cvzE47G9axFgGJLZuBtFZw&e=1758173337';

$cmd = $python . ' -W ignore ' . escapeshellarg($script) . ' ' . escapeshellarg($inputFile);

$output = [];
$code = 0;
exec($cmd, $output, $code);

// $output is an array of lines; we want the last line
$result = trim(end($output));

echo "stdout result: $result\n";

if ($result === "1") {
    echo "Speech detected\n";
} elseif ($result === "0") {
    echo "No speech\n";
} else {
    echo "Unexpected output\n";
}
?>
