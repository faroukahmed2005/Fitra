// Instagram API Integration
const INSTAGRAM_ACCESS_TOKEN = 'YOUR_LONG_LIVED_ACCESS_TOKEN'; // You'll need to replace this
const INSTAGRAM_BUSINESS_ACCOUNT_ID = '112671926910469';
const GRAPH_API_VERSION = 'v18.0';

async function getFollowersCount() {
    try {
        // First verify if the token is valid
        const tokenVerificationUrl = `https://graph.facebook.com/debug_token?input_token=${INSTAGRAM_ACCESS_TOKEN}&access_token=${INSTAGRAM_ACCESS_TOKEN}`;
        
        const tokenResponse = await fetch(tokenVerificationUrl);
        const tokenData = await tokenResponse.json();
        
        if (tokenData.data && tokenData.data.is_valid === false) {
            console.error('Access token is invalid or expired. Please generate a new long-lived token.');
            throw new Error('Invalid access token');
        }

        // If token is valid, fetch the followers count
        const igResponse = await fetch(
            `https://graph.facebook.com/${GRAPH_API_VERSION}/${INSTAGRAM_BUSINESS_ACCOUNT_ID}?fields=followers_count,username&access_token=${INSTAGRAM_ACCESS_TOKEN}`
        );
        
        const igData = await igResponse.json();
        console.log('Instagram Account Data:', igData);

        if (igData.error) {
            console.error('API Error:', igData.error);
            const followersElement = document.getElementById('followersCount');
            if (followersElement) {
                followersElement.textContent = '---';
            }
            return;
        }

        if (igData.followers_count !== undefined) {
            const followersElement = document.getElementById('followersCount');
            if (followersElement) {
                followersElement.textContent = igData.followers_count.toLocaleString();
                console.log('Successfully updated followers count to:', igData.followers_count);
            }
        } else {
            console.error('No followers count in response. API returned:', igData);
        }
    } catch (error) {
        console.error('Error fetching Instagram followers:', error);
        // Update UI to show error state
        const followersElement = document.getElementById('followersCount');
        if (followersElement) {
            followersElement.textContent = '---';
        }
    }
}

// Initialize counter
function initFollowersCounter() {
    console.log('Starting followers counter...');
    getFollowersCount();
    // Update every 5 minutes to avoid rate limiting
    setInterval(getFollowersCount, 300000);
}

// Start when DOM is loaded
document.addEventListener('DOMContentLoaded', initFollowersCounter); 