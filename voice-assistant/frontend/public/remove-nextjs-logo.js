// Script to dynamically remove Next.js logos
(function () {
  function removeNextJSLogo() {
    // Remove any SVG with Next.js logo characteristics
    const nextLogos = document.querySelectorAll(
      'svg[data-next-mark-loading], svg[width="40"][height="40"], svg[viewBox="0 0 40 40"]',
    );
    nextLogos.forEach((logo) => {
      logo.style.display = "none";
      logo.style.visibility = "hidden";
      logo.style.opacity = "0";
      logo.style.pointerEvents = "none";
      logo.style.position = "absolute";
      logo.style.left = "-9999px";
      logo.style.top = "-9999px";
      logo.style.zIndex = "-9999";
    });

    // Remove any element containing Next.js logo paths
    const allSvgs = document.querySelectorAll("svg");
    allSvgs.forEach((svg) => {
      const paths = svg.querySelectorAll("path");
      paths.forEach((path) => {
        const d = path.getAttribute("d") || "";
        if (
          d.includes("M13.3") ||
          d.includes("M11.825") ||
          d.includes("next_logo_paint")
        ) {
          svg.style.display = "none";
          svg.style.visibility = "hidden";
          svg.style.opacity = "0";
          svg.style.pointerEvents = "none";
          svg.style.position = "absolute";
          svg.style.left = "-9999px";
          svg.style.top = "-9999px";
          svg.style.zIndex = "-9999";
        }
      });
    });

    // Remove any element with Next.js related classes or attributes
    const nextElements = document.querySelectorAll(
      '[class*="next"], [class*="Next"], [data-next-mark-loading]',
    );
    nextElements.forEach((element) => {
      element.style.display = "none";
      element.style.visibility = "hidden";
      element.style.opacity = "0";
      element.style.pointerEvents = "none";
      element.style.position = "absolute";
      element.style.left = "-9999px";
      element.style.top = "-9999px";
      element.style.zIndex = "-9999";
    });
  }

  // Run immediately
  removeNextJSLogo();

  // Run on DOM changes
  const observer = new MutationObserver(removeNextJSLogo);
  observer.observe(document.body, {
    childList: true,
    subtree: true,
  });

  // Run periodically
  setInterval(removeNextJSLogo, 100);
})();
