import { Controller } from "stimulus";

export default class extends Controller {
  static targets = ["modal"];
  close(e) {
    e.preventDefault();
    this.modalTarget.classList.remove("is-active");
    const html = document.documentElement;
    html.classList.remove("is-clipped");
  }
}
