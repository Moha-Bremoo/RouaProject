"""
Ruua - Embedded Finance Platform UI
Beautiful Streamlit interface for loan offers, payments, and fraud detection
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
from main import (
    create_offer, process_payment, check_fraud,
    get_all_offers, get_all_transactions, get_all_fraud_checks,
    OfferRequest, PayRequest, FraudRequest
)

# Page configuration
st.set_page_config(
    page_title="Ruua - Embedded Finance Platform",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .success-card {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
    }
    .warning-card {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ffc107;
    }
    .danger-card {
        background-color: #f8d7da;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #dc3545;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'offers' not in st.session_state:
    st.session_state.offers = []
if 'transactions' not in st.session_state:
    st.session_state.transactions = []
if 'fraud_checks' not in st.session_state:
    st.session_state.fraud_checks = []

def main():
    # Header
    st.markdown('<h1 class="main-header">💰 Ruua - Embedded Finance Platform</h1>', unsafe_allow_html=True)
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page",
        ["🏠 Dashboard", "💳 Loan Offers", "💸 Payments", "🕵️ Fraud Detection", "📊 Admin Panel"]
    )
    
    if page == "🏠 Dashboard":
        show_dashboard()
    elif page == "💳 Loan Offers":
        show_loan_offers()
    elif page == "💸 Payments":
        show_payments()
    elif page == "🕵️ Fraud Detection":
        show_fraud_detection()
    elif page == "📊 Admin Panel":
        show_admin_panel()

def show_dashboard():
    """Main dashboard with overview metrics"""
    st.header("📊 Dashboard Overview")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Offers",
            value=len(st.session_state.offers),
            delta=None
        )
    
    with col2:
        st.metric(
            label="Total Transactions",
            value=len(st.session_state.transactions),
            delta=None
        )
    
    with col3:
        st.metric(
            label="Fraud Checks",
            value=len(st.session_state.fraud_checks),
            delta=None
        )
    
    with col4:
        total_amount = sum(t.get('amount', 0) for t in st.session_state.transactions)
        st.metric(
            label="Total Processed",
            value=f"${total_amount:,.2f}",
            delta=None
        )
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Offer status distribution
        if st.session_state.offers:
            offer_df = pd.DataFrame(st.session_state.offers)
            status_counts = offer_df['status'].value_counts()
            
            fig = px.pie(
                values=status_counts.values,
                names=status_counts.index,
                title="Loan Offer Status Distribution",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Fraud score distribution
        if st.session_state.fraud_checks:
            fraud_df = pd.DataFrame(st.session_state.fraud_checks)
            fig = px.histogram(
                fraud_df,
                x='fraud_score',
                title="Fraud Score Distribution",
                nbins=20,
                color_discrete_sequence=['#ff6b6b']
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Recent activity
    st.subheader("📈 Recent Activity")
    if st.session_state.offers:
        recent_offers = st.session_state.offers[-5:]
        for offer in reversed(recent_offers):
            status_emoji = {"approved": "✅", "approved_installments": "🔄", "manual_review": "⏳"}
            st.write(f"{status_emoji.get(offer['status'], '❓')} Offer {offer['offer_id'][:8]}... - {offer['status']} - ${offer['amount_offered']}")

def show_loan_offers():
    """Loan offer creation and management"""
    st.header("💳 Loan Offer Management")
    
    # Create new offer form
    with st.expander("➕ Create New Loan Offer", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            user_id = st.text_input("User ID", value="user_" + str(len(st.session_state.offers) + 1))
            order_amount = st.number_input("Order Amount ($)", min_value=0.01, value=500.0, step=0.01)
            recent_payments = st.number_input("Recent Successful Payments", min_value=0, value=2)
            failed_payments = st.number_input("Failed Payments (Last 30 days)", min_value=0, value=0)
        
        with col2:
            device_country = st.selectbox("Device Country", ["US", "CA", "UK", "DE", "FR", "AU", "JP"])
            billing_country = st.selectbox("Billing Country", ["US", "CA", "UK", "DE", "FR", "AU", "JP"])
            employer_enrolled = st.checkbox("Employer Enrolled in Salary Deduction")
            salary_monthly = st.number_input("Monthly Salary ($)", min_value=0.0, value=3000.0, step=100.0)
        
        if st.button("🚀 Create Loan Offer", type="primary"):
            try:
                offer_request = OfferRequest(
                    user_id=user_id,
                    order_amount=order_amount,
                    recent_payments=recent_payments,
                    failed_payments_last_30_days=failed_payments,
                    device_country=device_country,
                    billing_country=billing_country,
                    employer_enrolled=employer_enrolled,
                    salary_monthly=salary_monthly
                )
                
                offer = create_offer(offer_request)
                st.session_state.offers.append(offer)
                
                # Display result
                if offer['status'] == 'approved':
                    st.success(f"✅ Offer Approved! Amount: ${offer['amount_offered']}, Monthly Payment: ${offer['monthly_payment']}")
                elif offer['status'] == 'approved_installments':
                    st.success(f"🔄 Installment Offer Approved! Amount: ${offer['amount_offered']}, Monthly Payment: ${offer['monthly_payment']}")
                else:
                    st.warning(f"⏳ Manual Review Required: {offer['reason']}")
                
                st.json(offer)
                
            except Exception as e:
                st.error(f"Error creating offer: {str(e)}")
    
    # Display existing offers
    if st.session_state.offers:
        st.subheader("📋 Existing Offers")
        offers_df = pd.DataFrame(st.session_state.offers)
        
        # Filter options
        col1, col2 = st.columns(2)
        with col1:
            status_filter = st.selectbox("Filter by Status", ["All"] + list(offers_df['status'].unique()))
        with col2:
            sort_by = st.selectbox("Sort by", ["created_at", "amount_offered", "status"])
        
        # Apply filters
        filtered_df = offers_df.copy()
        if status_filter != "All":
            filtered_df = filtered_df[filtered_df['status'] == status_filter]
        
        # Display table
        st.dataframe(
            filtered_df[['offer_id', 'status', 'amount_offered', 'term_months', 'interest_rate', 'monthly_payment', 'reason']],
            use_container_width=True
        )

def show_payments():
    """Payment processing interface"""
    st.header("💸 Payment Processing")
    
    # Process payment form
    with st.expander("💳 Process Payment", expanded=True):
        if st.session_state.offers:
            # Filter approved offers only
            approved_offers = [o for o in st.session_state.offers if o['status'] in ['approved', 'approved_installments']]
            
            if approved_offers:
                offer_options = {f"{o['offer_id'][:8]}... - ${o['amount_offered']} ({o['status']})": o['offer_id'] for o in approved_offers}
                selected_offer = st.selectbox("Select Offer to Pay", list(offer_options.keys()))
                
                if st.button("💸 Process Payment", type="primary"):
                    try:
                        offer_id = offer_options[selected_offer]
                        pay_request = PayRequest(offer_id)
                        payment = process_payment(pay_request)
                        
                        if payment['success']:
                            st.session_state.transactions.append(payment)
                            st.success(f"✅ Payment Successful! Transaction ID: {payment['transaction_id']}")
                        else:
                            st.error(f"❌ Payment Failed: {payment['message']}")
                        
                        st.json(payment)
                        
                    except Exception as e:
                        st.error(f"Error processing payment: {str(e)}")
            else:
                st.warning("No approved offers available for payment")
        else:
            st.info("No offers available. Create a loan offer first.")
    
    # Display transactions
    if st.session_state.transactions:
        st.subheader("📋 Transaction History")
        transactions_df = pd.DataFrame(st.session_state.transactions)
        st.dataframe(transactions_df, use_container_width=True)

def show_fraud_detection():
    """Fraud detection interface"""
    st.header("🕵️ Fraud Detection System")
    
    # Fraud check form
    with st.expander("🔍 Run Fraud Check", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            user_id = st.text_input("User ID", value="user_" + str(len(st.session_state.fraud_checks) + 1))
            transaction_amount = st.number_input("Transaction Amount ($)", min_value=0.01, value=1000.0, step=0.01)
            device_country = st.selectbox("Device Country", ["US", "CA", "UK", "DE", "FR", "AU", "JP"])
        
        with col2:
            billing_country = st.selectbox("Billing Country", ["US", "CA", "UK", "DE", "FR", "AU", "JP"])
            device_count = st.number_input("Number of Devices", min_value=1, value=1)
            failed_payments = st.number_input("Failed Payments (Last 30 days)", min_value=0, value=0)
        
        if st.button("🕵️ Run Fraud Check", type="primary"):
            try:
                fraud_request = FraudRequest(
                    user_id=user_id,
                    transaction_amount=transaction_amount,
                    device_country=device_country,
                    billing_country=billing_country,
                    device_count=device_count,
                    failed_payments_last_30_days=failed_payments
                )
                
                fraud_check = check_fraud(fraud_request)
                st.session_state.fraud_checks.append(fraud_check)
                
                # Display result with appropriate styling
                if fraud_check['status'] == 'approved':
                    st.success(f"✅ Transaction Approved! Fraud Score: {fraud_check['fraud_score']}")
                elif fraud_check['status'] == 'suspicious':
                    st.warning(f"⚠️ Suspicious Transaction! Fraud Score: {fraud_check['fraud_score']} - Action: {fraud_check['action']}")
                else:
                    st.error(f"🚨 High Risk Transaction! Fraud Score: {fraud_check['fraud_score']} - Action: {fraud_check['action']}")
                
                if fraud_check['flags']:
                    st.write("🚩 **Fraud Flags:**")
                    for flag in fraud_check['flags']:
                        st.write(f"- {flag}")
                
                st.json(fraud_check)
                
            except Exception as e:
                st.error(f"Error running fraud check: {str(e)}")
    
    # Fraud analytics
    if st.session_state.fraud_checks:
        st.subheader("📊 Fraud Analytics")
        
        fraud_df = pd.DataFrame(st.session_state.fraud_checks)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Fraud status distribution
            status_counts = fraud_df['status'].value_counts()
            fig = px.pie(
                values=status_counts.values,
                names=status_counts.index,
                title="Fraud Check Results",
                color_discrete_map={
                    'approved': '#28a745',
                    'suspicious': '#ffc107',
                    'flagged': '#dc3545'
                }
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Fraud score over time
            fraud_df['created_at'] = pd.to_datetime(fraud_df['created_at'])
            fig = px.line(
                fraud_df,
                x='created_at',
                y='fraud_score',
                title="Fraud Score Over Time",
                color='status'
            )
            st.plotly_chart(fig, use_container_width=True)

def show_admin_panel():
    """Admin dashboard with all data"""
    st.header("📊 Admin Panel")
    
    # Summary statistics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Offers", len(st.session_state.offers))
    with col2:
        st.metric("Total Transactions", len(st.session_state.transactions))
    with col3:
        st.metric("Fraud Checks", len(st.session_state.fraud_checks))
    
    # Data tables
    tab1, tab2, tab3 = st.tabs(["Offers", "Transactions", "Fraud Checks"])
    
    with tab1:
        if st.session_state.offers:
            offers_df = pd.DataFrame(st.session_state.offers)
            st.dataframe(offers_df, use_container_width=True)
        else:
            st.info("No offers available")
    
    with tab2:
        if st.session_state.transactions:
            transactions_df = pd.DataFrame(st.session_state.transactions)
            st.dataframe(transactions_df, use_container_width=True)
        else:
            st.info("No transactions available")
    
    with tab3:
        if st.session_state.fraud_checks:
            fraud_df = pd.DataFrame(st.session_state.fraud_checks)
            st.dataframe(fraud_df, use_container_width=True)
        else:
            st.info("No fraud checks available")
    
    # Export data
    st.subheader("📤 Export Data")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Export Offers as CSV"):
            if st.session_state.offers:
                offers_df = pd.DataFrame(st.session_state.offers)
                csv = offers_df.to_csv(index=False)
                st.download_button(
                    label="Download Offers CSV",
                    data=csv,
                    file_name=f"offers_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
    
    with col2:
        if st.button("Export Transactions as CSV"):
            if st.session_state.transactions:
                transactions_df = pd.DataFrame(st.session_state.transactions)
                csv = transactions_df.to_csv(index=False)
                st.download_button(
                    label="Download Transactions CSV",
                    data=csv,
                    file_name=f"transactions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
    
    with col3:
        if st.button("Export Fraud Checks as CSV"):
            if st.session_state.fraud_checks:
                fraud_df = pd.DataFrame(st.session_state.fraud_checks)
                csv = fraud_df.to_csv(index=False)
                st.download_button(
                    label="Download Fraud Checks CSV",
                    data=csv,
                    file_name=f"fraud_checks_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )

if __name__ == "__main__":
    main()
