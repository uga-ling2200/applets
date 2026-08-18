(function () {
  "use strict";

  var script = document.currentScript;
  if (!script || document.querySelector(".applet-feedback-card")) {
    return;
  }

  var applet = script.dataset.applet || document.title || "Unknown applet";
  var repository = script.dataset.repository || "uga-ling2200/applets";
  var template = script.dataset.template || "applet-feedback.yml";
  var stylesheetUrl = new URL("feedback-card.css", script.src).href;

  if (!document.querySelector('link[data-applet-feedback-styles]')) {
    var stylesheet = document.createElement("link");
    stylesheet.rel = "stylesheet";
    stylesheet.href = stylesheetUrl;
    stylesheet.dataset.appletFeedbackStyles = "true";
    document.head.appendChild(stylesheet);
  }

  var issueUrl = new URL("https://github.com/" + repository + "/issues/new");
  issueUrl.searchParams.set("template", template);
  issueUrl.searchParams.set("title", "[Applet feedback] " + applet + ": ");
  issueUrl.searchParams.set("applet", applet);
  issueUrl.searchParams.set("source-url", window.location.href.split("#")[0]);

  var card = document.createElement("section");
  card.className = "applet-feedback-card";
  card.setAttribute("aria-labelledby", "applet-feedback-heading");

  var content = document.createElement("div");
  content.className = "applet-feedback-card__content";

  var copy = document.createElement("div");
  var heading = document.createElement("h2");
  heading.id = "applet-feedback-heading";
  heading.textContent = "Help us improve this applet";

  var description = document.createElement("p");
  description.textContent =
    "Found a problem, unclear instruction, or accessibility issue? Send feedback using our shared GitHub form.";

  var button = document.createElement("a");
  button.className = "applet-feedback-card__button";
  button.href = issueUrl.toString();
  button.target = "_blank";
  button.rel = "noopener noreferrer";
  button.textContent = "Report a problem or give feedback";
  button.setAttribute("aria-label", "Report feedback for " + applet + " on GitHub");

  copy.appendChild(heading);
  copy.appendChild(description);
  content.appendChild(copy);
  content.appendChild(button);
  card.appendChild(content);
  document.body.appendChild(card);
})();
