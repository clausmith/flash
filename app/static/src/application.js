import "./scss/app.scss";

import { Application } from "stimulus";
import { definitionsFromContext } from "stimulus/webpack-helpers";

const application = Application.start();
const context = require.context("./controllers", true, /\.js$/);
application.load(definitionsFromContext(context));

document.addEventListener("DOMContentLoaded", () => {
  (document.querySelectorAll(".notification .delete") || []).forEach(
    ($delete) => {
      const notification = $delete.parentNode;

      $delete.addEventListener("click", () => {
        notification.parentNode.removeChild(notification);
      });
    }
  );
});
