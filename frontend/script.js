document.getElementById('voucher-form').addEventListener('submit', async function (e) {
    e.preventDefault();
    const code = document.getElementById('voucher-code').value;

    const response = await fetch('/check-voucher', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({code: code})
    });

    const result = await response.json();
    const output = document.getElementById('result');

    if (result.valid) {
        output.textContent = `✅ Valid voucher (${result.type}, expires on ${result.expires})`;
        output.style.color = 'green';
    } else {
        output.textContent = '❌ Invalid or expired voucher.';
        output.style.color = 'red';
    }
});