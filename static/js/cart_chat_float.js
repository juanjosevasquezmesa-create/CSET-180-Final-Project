// Cart and Chat Popup Toggle Functionality

document.addEventListener('DOMContentLoaded', function() {
    const cartToggleBtn = document.getElementById('cart-toggle-btn');
    const cartPopup = document.getElementById('cart-popup');
    const cartCloseBtn = document.getElementById('cart-close-btn');
    
    const chatToggleBtn = document.getElementById('chat-toggle-btn');
    const chatPopup = document.getElementById('chat-popup');
    const chatCloseBtn = document.getElementById('chat-close-btn');
    
    // Track active chat complaints in sessionStorage
    let activeComplaints = JSON.parse(sessionStorage.getItem('activeComplaints')) || [];
    
    // Cart Toggle
    if (cartToggleBtn) {
        cartToggleBtn.addEventListener('click', function() {
            cartPopup.classList.toggle('hidden');
            if (!cartPopup.classList.contains('hidden')) {
                loadCartItems();
            }
        });
    }
    
    if (cartCloseBtn) {
        cartCloseBtn.addEventListener('click', function() {
            cartPopup.classList.add('hidden');
        });
    }
    
    // Chat Toggle
    if (chatToggleBtn) {
        chatToggleBtn.addEventListener('click', function() {
            if (activeComplaints.length === 0) {
                displayChatMessage('No active chats. Open a complaint from your account or order details page.');
                chatPopup.classList.remove('hidden');
            } else {
                chatPopup.classList.toggle('hidden');
                if (!chatPopup.classList.contains('hidden')) {
                    // Load the first complaint's messages
                    loadComplaintMessages(activeComplaints[0]);
                }
            }
        });
    }
    
    if (chatCloseBtn) {
        chatCloseBtn.addEventListener('click', function() {
            chatPopup.classList.add('hidden');
            // Clear UI only, not database
            activeComplaints = [];
            sessionStorage.removeItem('activeComplaints');
            updateChatBubbleVisibility();
        });
    }
    
    // Open chat for a complaint (called from other pages)
    window.openComplaintChat = function(complaintId) {
        if (!activeComplaints.includes(complaintId)) {
            activeComplaints.push(complaintId);
            sessionStorage.setItem('activeComplaints', JSON.stringify(activeComplaints));
        }
        updateChatBubbleVisibility();
        chatPopup.classList.remove('hidden');
        loadComplaintMessages(complaintId);
    };
    
    // Update chat bubble visibility
    function updateChatBubbleVisibility() {
        if (activeComplaints.length > 0) {
            chatToggleBtn.style.display = 'flex';
        } else {
            chatToggleBtn.style.display = 'none';
        }
    }
    
    // Update on page load if there are active complaints
    updateChatBubbleVisibility();
    
    // Load cart items via API
    async function loadCartItems() {
        try {
            const response = await fetch('/api/cart/items');
            const data = await response.json();
            
            if (data.error) {
                displayCartError(data.error);
                return;
            }
            
            displayCartItems(data);
        } catch (error) {
            console.error('Error loading cart:', error);
        }
    }
    
    // Display cart items (view only)
    function displayCartItems(data) {
        const cartItemsContainer = document.getElementById('cart-items-container');
        const cartTotalContainer = document.getElementById('cart-total');
        
        if (!cartItemsContainer) return;
        
        if (data.items.length === 0) {
            cartItemsContainer.innerHTML = '<p class="empty-cart-msg">Your cart is empty</p>';
            cartTotalContainer.innerHTML = '';
            return;
        }
        
        let itemsHTML = '';
        data.items.forEach(item => {
            itemsHTML += `
                <div class="cart-item">
                    <div class="cart-item-info">
                        <h4>${item.model}</h4>
                        <p>${item.year} • ${item.color}</p>
                        <p>$${item.price.toFixed(2)} x ${item.quantity}</p>
                    </div>
                    <div class="cart-item-total">
                        <p>$${item.item_total.toFixed(2)}</p>
                    </div>
                </div>
            `;
        });
        
        cartItemsContainer.innerHTML = itemsHTML;
        
        cartTotalContainer.innerHTML = `
            <div class="cart-footer">
                <p class="cart-total">Total: $${data.total_price.toFixed(2)}</p>
                <a href="/checkout" class="checkout-btn">Proceed to Checkout</a>
            </div>
        `;
    }
    
    // Display cart error
    function displayCartError(error) {
        const cartItemsContainer = document.getElementById('cart-items-container');
        if (cartItemsContainer) {
            cartItemsContainer.innerHTML = `<p class="cart-error">${error}</p>`;
        }
    }
    
    // Load messages for a specific complaint
    async function loadComplaintMessages(complaintId) {
        try {
            const response = await fetch(`/api/chat/messages/${complaintId}`);
            const data = await response.json();
            
            if (data.error) {
                displayChatError(data.error);
                return;
            }
            
            displayComplaintMessages(data, complaintId);
        } catch (error) {
            console.error('Error loading messages:', error);
        }
    }
    
    // Display complaint messages thread with tabs
    function displayComplaintMessages(data, complaintId) {
        const chatMessagesContainer = document.getElementById('chat-messages-container');
        const chatInputContainer = document.getElementById('chat-input-container');
        const chatHeaderContainer = document.getElementById('chat-header-container');
        
        if (!chatMessagesContainer) return;
        
        // Display tabs
        let tabsHTML = '<div class="chat-tabs">';
        activeComplaints.forEach(id => {
            const isActive = id === complaintId ? 'active' : '';
            const tabTitle = id === data.complaint.complaint_id ? data.complaint.title : `Complaint #${id}`;
            tabsHTML += `
                <div class="chat-tab ${isActive}" data-complaint-id="${id}">
                    <span>${tabTitle}</span>
                    <button class="tab-close-btn" data-complaint-id="${id}">×</button>
                </div>
            `;
        });
        tabsHTML += '</div>';
        
        if (chatHeaderContainer) {
            chatHeaderContainer.innerHTML = tabsHTML;
            
            // Add tab click listeners
            document.querySelectorAll('.chat-tab').forEach(tab => {
                tab.addEventListener('click', function(e) {
                    if (!e.target.classList.contains('tab-close-btn')) {
                        loadComplaintMessages(this.dataset.complaintId);
                    }
                });
            });
            
            // Add tab close listeners
            document.querySelectorAll('.tab-close-btn').forEach(btn => {
                btn.addEventListener('click', function(e) {
                    e.stopPropagation();
                    const cId = this.dataset.complaintId;
                    activeComplaints = activeComplaints.filter(id => id != cId);
                    sessionStorage.setItem('activeComplaints', JSON.stringify(activeComplaints));
                    
                    if (activeComplaints.length === 0) {
                        chatPopup.classList.add('hidden');
                        updateChatBubbleVisibility();
                    } else {
                        loadComplaintMessages(activeComplaints[0]);
                    }
                });
            });
        }
        
        // Display messages
        let messagesHTML = `<div class="messages-thread">`;
        
        data.messages.forEach(msg => {
            const msgClass = msg.is_current_user ? 'user-message' : 'other-message';
            messagesHTML += `
                <div class="message ${msgClass}">
                    <p class="message-sender">${msg.sender_name}</p>
                    <p class="message-text">${msg.message_text}</p>
                    <p class="message-time">${new Date(msg.sent_at).toLocaleString()}</p>
                </div>
            `;
        });
        
        messagesHTML += '</div>';
        chatMessagesContainer.innerHTML = messagesHTML;
        
        // Scroll to bottom
        setTimeout(() => {
            const thread = chatMessagesContainer.querySelector('.messages-thread');
            if (thread) thread.scrollTop = thread.scrollHeight;
        }, 100);
        
        // Update input container
        if (chatInputContainer) {
            chatInputContainer.innerHTML = `
                <form class="message-form" data-complaint-id="${data.complaint.complaint_id}">
                    <input type="text" class="message-input" placeholder="Type a message..." required />
                    <button type="submit" class="send-message-btn">Send</button>
                </form>
            `;
            
            // Add form submit listener
            document.querySelector('.message-form').addEventListener('submit', function(e) {
                e.preventDefault();
                const cId = this.dataset.complaintId;
                const messageInput = this.querySelector('.message-input');
                const message = messageInput.value.trim();
                
                if (message) {
                    sendMessage(cId, message);
                    messageInput.value = '';
                }
            });
        }
    }
    
    // Send message to complaint
    async function sendMessage(complaintId, message) {
        try {
            const response = await fetch(`/api/chat/send-message/${complaintId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: message }),
            });
            
            const data = await response.json();
            
            if (data.success) {
                loadComplaintMessages(complaintId);
            } else {
                displayChatError(data.error);
            }
        } catch (error) {
            console.error('Error sending message:', error);
        }
    }
    
    // Display chat message
    function displayChatMessage(msg) {
        const chatMessagesContainer = document.getElementById('chat-messages-container');
        if (chatMessagesContainer) {
            chatMessagesContainer.innerHTML = `<p class="chat-message-info">${msg}</p>`;
        }
    }
    
    // Display chat error
    function displayChatError(error) {
        const chatMessagesContainer = document.getElementById('chat-messages-container');
        if (chatMessagesContainer) {
            chatMessagesContainer.innerHTML = `<p class="chat-error">${error}</p>`;
        }
    }
});
