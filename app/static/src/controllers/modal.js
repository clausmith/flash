import { Controller } from "stimulus";

export default class extends Controller {
  static targets = ["modal"];

  close(e) {
    e.preventDefault();

    const html = document.documentElement;
    this.modalTarget.classList.remove("is-active");
    html.classList.remove("is-clipped");
  }
}
