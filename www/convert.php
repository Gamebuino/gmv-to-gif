<?php
error_reporting(E_ALL);
include_once(realpath(dirname(__FILE__)).'/constants.php');


if (!file_exists($ID_FILE)) {
	file_put_contents($ID_FILE, 0);
}

if (!file_exists($UPLOAD_FILE)) {
	file_put_contents($UPLOAD_FILE, '{}');
}

$error = '';
$gif_url = '';
$id = -1;
if (isset($_FILES['up']) && is_uploaded_file($_FILES['up']['tmp_name'])) {
	if (preg_match('#([ !\#$%\'()+-.\d;=@-\[\]-{}~]+)\.(\w+)$#', $_FILES['up']['name'], $name)) {
		$ext = strtolower($name[2]);
		if ($ext == 'bmp' || $ext == 'gmv') {
			
			// grab file ID and update metadata
			$id = (int)file_get_contents($ID_FILE);
			file_put_contents($ID_FILE, $id+1);
			$json = json_decode(file_get_contents($UPLOAD_FILE), true);
			$json[$id] = time();
			file_put_contents($UPLOAD_FILE, json_encode($json));
			
			$fpath = $UPLOAD_DIR.$id.'/in.'.$ext;
			mkdir($UPLOAD_DIR.$id);
			if (move_uploaded_file($_FILES['up']['tmp_name'], $fpath)) {
				$h = substr(file_get_contents($fpath), 0, 2);
				if (($ext == 'bmp' && $h == 'BM') || ($ext == 'gmv' && $h == 'GV')) {
					$out = [];
					$ret_var = 0;
					if ($ext == 'gmv') {
						exec('python3 GMVtoBMP.py '.escapeshellarg($UPLOAD_DIR.$id), $out, $ret_var);
						if ($ret_var) {
							$error = implode("\n", $out);
						}
						$out = [];
					}
					if (!$ret_var) {
						exec('python3 BMPtoGif.py '.escapeshellarg($UPLOAD_DIR.$id), $out, $ret_var);
						if ($ret_var) {
							$error = implode("\n", $out);
						}
					}
					if (!$ret_var) {
						$gif_url = 'uploads/'.$id.'/out.gif';
					}
				} else {
					$error = 'invalid file';
				}
			} else {
				$error = 'failed to move uploaded file';
			}
		} else {
			$error = 'inalid file';
		}
	} else {
		$error = 'invalid file name';
	}
} else {
	$error = 'no file provided';
}
if ($id == -1 || !$gif_url) {
	$error = 'something went wrong';
}

if (isset($_GET['json'])) {
	header('Content-Type: application/json');
	echo json_encode([
		'success' => $error?false:true,
		'error' => $error,
		'id' => $id,
		'gif_url' => $gif_url,
	]);
	exit;
}
if ($error) {
	header('Location: index.php?error='.urlencode($error));
} else {
	header('Location: index.php?id='.urlencode($id));
}
