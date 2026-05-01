document.addEventListener('DOMContentLoaded', () => {
    const money = new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
    });

    function updateSubtotal() {
        let subtotal = 0;

        document.querySelectorAll('.cart-row').forEach(row => {
            const input = row.querySelector('.quantity-input');
            const rowTotal = row.querySelector('.cart-row-total p');
            const price = Number(input.dataset.price);
            const quantity = Number(input.value);
            const total = price * quantity;

            subtotal += total;
            rowTotal.textContent = money.format(total);
        });

        const subtotalEl = document.getElementById('cart-subtotal');
        if (subtotalEl) {
            subtotalEl.textContent = money.format(subtotal);
        }
    }

    async function saveQuantity(row, quantity) {
        const response = await fetch(`/api/cart/items/${row.dataset.cartItemId}`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ quantity }),
        });

        const data = await response.json();

        if (!response.ok || data.error) {
            throw new Error(data.error || 'Could not update cart.');
        }
    }

    document.querySelectorAll('.cart-row').forEach(row => {
        const input = row.querySelector('.quantity-input');
        const buttons = row.querySelectorAll('.quantity-btn');
        const removeButton = row.querySelector('.remove-item-btn');

        async function setQuantity(nextQuantity) {
            const min = Number(input.min);
            const max = Number(input.max);
            const previousQuantity = Number(input.value);
            const quantity = Math.min(Math.max(nextQuantity, min), max);

            input.value = quantity;
            updateSubtotal();

            try {
                await saveQuantity(row, quantity);
            } catch (error) {
                input.value = previousQuantity;
                updateSubtotal();
                alert(error.message);
            }
        }

        buttons.forEach(button => {
            button.addEventListener('click', () => {
                setQuantity(Number(input.value) + Number(button.dataset.change));
            });
        });

        input.addEventListener('change', () => {
            setQuantity(Number(input.value));
        });

        removeButton.addEventListener('click', async () => {
            const response = await fetch(`/api/cart/items/${row.dataset.cartItemId}`, {
                method: 'DELETE',
            });
            const data = await response.json();

            if (!response.ok || data.error) {
                alert(data.error || 'Could not remove item.');
                return;
            }

            row.remove();
            updateSubtotal();

            if (!document.querySelector('.cart-row')) {
                window.location.reload();
            }
        });
    });
});
