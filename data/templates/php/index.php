<?php
$image = "logo.png";

$og_site_name = "NSG Comprehensive Rules";
$og_title = "NSG Comprehensive Rules";
$og_description = "Description";

if(isset($_GET['r'])) {
    $rule = $_GET['r'];
} else {
    $rule = '';
}

$path = 'rules.json';
$jsonString = file_get_contents($path);
$jsonData = json_decode($jsonString, true);

function search_for_rule($jsonData, $key, $value) {
    foreach($jsonData as $r){
        if($r[$key] == $value) {
            return $r; 
        }
    }
}

$og_desc = "Access the complete rules framework that makes Netrunner click.";
$jsonRule = null;
if($rule) {
    $jsonRule = search_for_rule($jsonData, 'id', $rule);
}

if($jsonRule) {
    /* Three different scenarios:
        $jsonRule is level 1 (i.e. chapter):
            - og:title will be $jsonRule
            - og:description will be empty
        $jsonRule is level 2 (i.e. subchapter):
            - og:title will be $jsonRule
            - og:description will be its children
        $jsonRule is level 3 or deeper (i.e. subrule):
            - og:title will be the parent section
            - og:description will be $jsonRule and its children
    */
    $level = count(explode('.', $jsonRule['nr']));

    if($level == 1) {
        $og_title = $jsonRule['nr'].". ".$jsonRule['text'];
        $og_desc = "";
    } else {
        if($level == 2) {
            $og_title = $jsonRule['nr'].". ".$jsonRule['text'];
            $skipSelf = true;
        }
        if($level > 2) {
            // Look for parent section and display it as title
            $sectionNR = join('.',array_slice(explode('.', $jsonRule['nr']), 0, -1));
            $jsonSection = search_for_rule($jsonData, 'nr', $sectionNR);
            
            $og_title = $jsonSection['nr'].". ".$jsonSection['text'];
            $skipSelf = false;
        }

        // Fill text with this item and its children
        $out = "";
        function appendItem(&$out, &$jsonData, $jsonElem, $skipSelf){
            if(strlen($out) > 500) {
                return;
            }
            if(!$skipSelf){
                $out = $out." ".$jsonElem['nr'].". ".$jsonElem['text'];
            }
            foreach($jsonElem['children'] as $id) {
                $childElem = search_for_rule($jsonData, 'id', $id);
                if($childElem) {
                    appendItem($out, $jsonData, $childElem, false);
                }
            }
        }
        appendItem($out, $jsonData, $jsonRule, $skipSelf);

        $og_desc = trim($out);
    }
}

$doc = new DOMDocument('1.0', 'UTF-8');
$internalErrors = libxml_use_internal_errors(true);
$doc->loadHTMLFile("rules.html");

$head = $doc->getElementsByTagName('head')[0];

$metaProps = array();
$metaProps[] = array("property" => "og:title", "content" => $og_title);
$metaProps[] = array("property" => "og:type", "content" => "website");
$metaProps[] = array("property" => "og:image", "content" => "https://dumpyard.lostgeek.de/rules/logo.png");
$metaProps[] = array("property" => "og:site_name", "content" => $og_site_name);
$metaProps[] = array("property" => "og:description", "content" => $og_desc);


foreach($metaProps as $entry) {
    $el = $doc->createElement('meta');
    $el->setAttribute('property', $entry['property']);
    $el->setAttribute('content', $entry['content']);
    $head->appendChild($el);
}


echo $doc->saveHTML();
?>
