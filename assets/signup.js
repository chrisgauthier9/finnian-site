/* Mailing-list signup.
   Set SIGNUP_ENDPOINT to the provider's form action once the account exists
   (MailerLite embedded form -> "Form action URL"). Until then the form falls
   back to a pre-filled email to contact@finnian.ca, so it is never a dead end. */

const SIGNUP_ENDPOINT = ""; // e.g. "https://assets.mailerlite.com/jsonp/000000/forms/000000/subscribe"
const FALLBACK_ADDRESS = "contact@finnian.ca";

document.querySelectorAll("[data-signup]").forEach((form) => {
  const status = form.querySelector("[data-status]");
  const input = form.querySelector('input[type="email"]');
  const button = form.querySelector('button[type="submit"]');

  const say = (message) => { if (status) status.textContent = message; };

  form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = input.value.trim();
    if (!email || !input.checkValidity()) {
      say("That does not look like an email address.");
      input.focus();
      return;
    }

    if (!SIGNUP_ENDPOINT) {
      // No provider wired up yet: open the reader's mail client instead of failing silently.
      const subject = encodeURIComponent("Add me to the list");
      const body = encodeURIComponent(`Please add ${email} to the Finnian mailing list.`);
      window.location.href = `mailto:${FALLBACK_ADDRESS}?subject=${subject}&body=${body}`;
      say("Opening your mail app.");
      return;
    }

    button.disabled = true;
    say("One moment.");

    try {
      const body = new FormData();
      body.append("fields[email]", email);
      const response = await fetch(SIGNUP_ENDPOINT, { method: "POST", body });
      if (!response.ok) throw new Error(String(response.status));
      form.reset();
      say("You are on the list. Check your inbox for the remixes.");
    } catch (error) {
      say(`Something went wrong. Email ${FALLBACK_ADDRESS} and I will add you.`);
      button.disabled = false;
    }
  });
});
