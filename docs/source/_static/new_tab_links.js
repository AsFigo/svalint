(function () {
    function applyNewTabLinks() {
        document.querySelectorAll('a[href^="http"]').forEach(function (link) {
            link.setAttribute('target', '_blank');
            link.setAttribute('rel', 'noopener noreferrer');
        });
    }

    // If the script is deferred, DOMContentLoaded may have already fired.
    // Check readyState and run immediately if the DOM is already parsed.
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', applyNewTabLinks);
    } else {
        applyNewTabLinks();
    }
})();
