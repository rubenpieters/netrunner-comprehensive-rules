function closeToc() {
    const parent = document.querySelector("#RulesParent");
    parent.removeAttribute("data-tocopen");
}
function openToc() {
    const parent = document.querySelector("#RulesParent");
    parent.setAttribute("data-tocopen", "");
}

// Mobile version has a backdrop, which can also close the TOC.
document.getElementById('TocBackdrop').addEventListener('click', closeToc);

// Close TOC immediately on mobile after navigation to a section.
document.querySelector('#RulesToc nav').addEventListener('click', function(e) {
  if (e.target.closest('a') && window.innerWidth < 1024) closeToc();
});

addEventListener("load", (event) => {
    const urlParams = new URLSearchParams(window.location.search);
    const ruleId = urlParams.get('r');
    const element = document.getElementById(ruleId);
    if(ruleId) {
        // Timeout seems to be necessary, because without it the scrolling sometimes
        // could happen before the element was fully loaded. This meant that the
        // scrollIntoView didn't move to exactly the right place it should.
        setTimeout(() => {
          document.getElementById(ruleId)?.scrollIntoView();
        }, 10);
    }
});

// Prevent reloading page while following rules links
// The rule link still appears in the user's navigation bar to copy and paste 
const $elems = document.querySelectorAll('a.RuleLink')
const elems = Array.from($elems)
elems.forEach(a => {
    url = new URL(a.href);
    url.search = url.hash.replace('#', '?r=');
    url.hash = "";
    a.href = url.href;
    a.onclick = (e) => {
        // do not follow link
        e.preventDefault();

        // replace url in nav bar
        history.replaceState(null, null, a.href);

        // Replace link symbol with clipboard symbol
        navigator.clipboard?.writeText(a.href).catch(() => {});
        const link  = a.parentElement.querySelector('.RuleLinkSymbol--link');
        const check = a.parentElement.querySelector('.RuleLinkSymbol--check');
        link.setAttribute('hidden', '');
        check.removeAttribute('hidden');

        // Revert back to link symbol after 1s
        setTimeout(() => {
            link.removeAttribute('hidden');
            check.setAttribute('hidden', '');
        }, 1000);
    }
})

jQuery(document).ready(function($){
    $('.Thumbnail').hover(function(){
        const data_src = $(this).children('.ThumbnailImageContainer').children('img').attr('data-src');
        $(this).children('.ThumbnailImageContainer').children('img').attr('src', data_src);
    });
});

function buildPartialMatchFromWordStartExpression(searchValue) {
    return new RegExp(`(?<=^|\\s|\\>|"|\\()${RegExp.escape(searchValue)}`, 'i');
};

function buildAllPartialMatchesFromWordStartExpression(searchValue) {
    return new RegExp(`(?<=^|\\s|\\>|"|\\()${RegExp.escape(searchValue)}`, 'gi');
};

function buildExactMatchExpression(searchValue) {
    return new RegExp(`(?<=^)${RegExp.escape(searchValue)}(?=$)`, 'i');
};

function buildAllMatchesExpression(searchValue) {
    return new RegExp(RegExp.escape(searchValue), 'gi');
};

// Recursively extracts text nodes from nested elements so that search terms match only against text within elements and not the elements themselves
jQuery.fn.extractNestedTextNodes = function() {
    const textNodes = [];

    this.each(function() {
        // The RuleLinkSymbol element contains a hidden text node that returns a false positive when searching "link", this logic ignores this element
        if ($(this).get(0).nodeType === Node.TEXT_NODE && !$(this).parent().is('.RuleLinkSymbol')) {
            textNodes.push($(this));
        } else if ($(this).get(0).nodeType === Node.ELEMENT_NODE) {
            const nestedTextNodes = $(this).contents().extractNestedTextNodes();
            textNodes.push(...nestedTextNodes);
        };
    });

    return textNodes;
}

jQuery.fn.addHighlightsToRule = function(textToHighlight) {
    const allPartialMatchesFromWordStart = buildAllPartialMatchesFromWordStartExpression(textToHighlight);

    // Extraction required in order to handle various ways in which text and elements are nested, avoiding false positives and layout breaking changes
    this.extractNestedTextNodes().forEach(function($node) {
        const nodeText = $node.get(0).nodeValue;

        if (allPartialMatchesFromWordStart.test(nodeText)) {
            const highlightedHTML = nodeText.replace(allPartialMatchesFromWordStart, match => `<span class="Highlight">${match}</span>`);
            // Creates throw away wrapper to inject highlighted element into text node 
            const $wrapper = $('<span></span>').html(highlightedHTML);
            $node.replaceWith($wrapper.contents());
        };
    });
};

jQuery.fn.removeHighlightsFromRule = function(textToRemoveHightlight) {    
    let textWithHighlightsRemoved = this.html().replace(buildAllMatchesExpression(`<span class="Highlight">${textToRemoveHightlight}</span>`), function(match) {
        return match.replace('<span class="Highlight">', '').replace('</span>', '');
    });
    
    this.html(textWithHighlightsRemoved);
};

// Returns false if no chapter heading is found before running out of siblings
jQuery.fn.findChapterHeading = function() {
    if ($.isEmptyObject(this.prev())) {
        return false;
    } else if (this.prev().is(".Chapter")) {
        return this.prev();
    };

    return this.prev().findChapterHeading();
};

// Returns false if no section heading is found before finding a chapter heading or running out of siblings
jQuery.fn.findSectionHeading = function() {
    if ($.isEmptyObject(this.prev()) | this.prev().is(".Chapter")) {
        return false;
    } else if (this.prev().is(".Section")) {
        return this.prev();
    }
    
    return this.prev().findSectionHeading();
};

jQuery.fn.showHeadingsForEachRule = function() {
    return this.each(function() {
        const $chapterHeading = $(this).findChapterHeading();

        if ($chapterHeading) {
            $chapterHeading.show();

            const [tocChapterReference] = $chapterHeading.text().split('. ');
            $(".RulesTocList>li>a").filter(function() {
                return $(this).text().startsWith(`${tocChapterReference} `);
            }).parent().show();
        }

        const $sectionHeading = $(this).findSectionHeading();

        if ($sectionHeading) {
            $sectionHeading.show();

            const [tocSectionReference] = $sectionHeading.text().split('. ');
            $(".RulesTocList>li>a").filter(function() {
                return $(this).text().startsWith(`${tocSectionReference} `);
            }).parent().show();
        }

        if ($(this).prev().is(".Snippet")) {
            $(this).prev().show();
        };
    });
};

jQuery.fn.executeSearch = function(searchValue) {

    if (searchValue !== '') {
        const exactMatch = buildExactMatchExpression(searchValue);

        const matchingTags = $("#SelectedTags>.CustomTag").filter(function() {
            return exactMatch.test($(this).text());
        })

        if (matchingTags.length === 0) {
            $(".TitleContainer").hide();
            $("main").children().hide();
            $(".RulesTocList>li").hide();
            
            $("#SelectedTags").append(`<li class="CustomTag"><svg class="CustomTagIcon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 384 512"><path d="M342.6 150.6c12.5-12.5 12.5-32.8 0-45.3s-32.8-12.5-45.3 0L192 210.7 86.6 105.4c-12.5-12.5-32.8-12.5-45.3 0s-12.5 32.8 0 45.3L146.7 256 41.4 361.4c-12.5 12.5-12.5 32.8 0 45.3s32.8 12.5 45.3 0L192 301.3 297.4 406.6c12.5 12.5 32.8 12.5 45.3 0s12.5-32.8 0-45.3L237.3 256 342.6 150.6z"/></svg>${searchValue}</li>`);

            const selectedTagExpressions = $.map($("#SelectedTags>.CustomTag"), function(tag) {
                return buildPartialMatchFromWordStartExpression($(tag).text());
            });

            const $selectedRules = $("main>.Rules").filter(function() {
                let aRuleContainsSelectedTags = false;

                $(this).children(".Rule").each(function() {
                    const $rule = $(this);

                    const textNodes = $(this).extractNestedTextNodes()
                    
                    const allTagsMatch = selectedTagExpressions.every((selectedTagExpression) => {
                        return textNodes.some((textNode) => {
                            return selectedTagExpression.test(textNode.get(0).nodeValue)
                        })
                    });
                    
                    $rule.addHighlightsToRule(searchValue);

                    if (allTagsMatch) {            
                        $rule.show();
                        aRuleContainsSelectedTags = true;
                    } else {
                        $rule.hide();
                    };
                });

                return aRuleContainsSelectedTags;
            })

            $selectedRules.showHeadingsForEachRule();

            $selectedRules.show();
        }
        
        $('#SearchInput').val('');
    };
}

jQuery(document).ready(function($) {

    // Toggles search bar and tags visibility
    $('#SearchToolBar').on("click", function() {
        $('#SearchBar').toggleClass('display-flex')
        $('#SelectedTagsContainer').toggle()
    })

    $('#SearchInput').on("keyup", function(e) {
        if (e.key === 'Enter') {
            const searchValue = $(this).val();

            $(this).executeSearch(searchValue);
        }
    });

    $('#SearchButton').on("click", function() {
        const searchValue = $('#SearchInput').val();

        $('#SearchInput').executeSearch(searchValue);
    })

    // Handles tag deselection, removing from selected tags list
    $("#SelectedTags").on('click', '.CustomTag', function() {
        const $clickedTag = $(this);

        const $filteredTags = $("#SelectedTags>.CustomTag").filter(function() {
                return $(this).text() !== $clickedTag.text()
            })

        if ($filteredTags.length) {
            const selectedTagExpressions = $.map($filteredTags, function(tag) {
                return buildPartialMatchFromWordStartExpression($(tag).text());
            });

            const $selectedRules = $("main>.Rules").filter(function() {      
                let aRuleContainsSelectedTags = false;

                $(this).children(".Rule").each(function() {
                    const $rule = $(this);
                    $rule.removeHighlightsFromRule($clickedTag.text());

                    const textNodes = $(this).extractNestedTextNodes();
                    const allTagsMatch = selectedTagExpressions.every((selectedTagExpression) => {
                        return textNodes.some((textNode) => {
                            return selectedTagExpression.test(textNode.get(0).nodeValue);
                        });
                    });
                    
                    if (allTagsMatch) {            
                        $rule.show();
                        aRuleContainsSelectedTags = true;
                    } else {
                        $rule.hide();
                    };
                });

                return aRuleContainsSelectedTags;    
            });

            $selectedRules.showHeadingsForEachRule();

            $selectedRules.show();
        } else {
            $(".TitleContainer").show();
            $("main").children().show();
            $(".RulesTocList>li").show();
            $("main>ol>li").each(function() {
                $(this).show();
                $(this).removeHighlightsFromRule($clickedTag.text());
            });
        };

        $clickedTag.remove();
    });
});
