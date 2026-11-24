(() => {
  const form = document.getElementById("contact-form");
  const name = document.getElementById("contact-name");
  const message = document.getElementById("contact-message");
  const status = document.getElementById("contact-status");
  const manualCopy = document.getElementById("contact-manual-copy");
  const draft = document.getElementById("contact-draft");

  form.addEventListener("input", () => {
    message.setCustomValidity("");
    status.textContent = "";
    manualCopy.hidden = true;
    draft.value = "";
  });

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const body = message.value.trim();
    if (!body) {
      message.setCustomValidity("Enter a short message for Jennifer.");
      message.reportValidity();
      return;
    }

    const signature = name.value.trim();
    const text = ["Hi Jennifer,", body, signature].filter(Boolean).join("\n\n");

    try {
      await navigator.clipboard.writeText(text);
      manualCopy.hidden = true;
      status.textContent = "Message copied. Open Jennifer’s LinkedIn profile and paste it into a message.";
    } catch {
      manualCopy.hidden = false;
      draft.value = text;
      draft.focus();
      draft.select();
      status.textContent = "Copy the selected draft, then paste it into a LinkedIn message to Jennifer.";
    }
  });

  form.hidden = false;
})();
