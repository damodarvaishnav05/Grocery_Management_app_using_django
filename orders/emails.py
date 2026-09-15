import urllib.parse
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils import timezone


def get_site_base_url():
    """Resolve site base domain for absolute links"""
    render_host = getattr(settings, "RENDER_EXTERNAL_HOSTNAME", "")
    if render_host:
        return f"https://{render_host}"
    return "https://om-super-mart.onrender.com"


def send_owner_new_order_email(order, payment_method="Online Payment"):
    """
    Sends an urgent, high-priority order notification to the store owner/delivery partner
    (damodar4162@gmail.com) with customer address, Google Maps directions, and item list.
    """
    owner_email = getattr(settings, "OWNER_NOTIFICATION_EMAIL", "damodar4162@gmail.com")
    if not owner_email:
        return False

    full_address = f"{order.address}, {order.city}, {order.state} - {order.pincode}"
    encoded_destination = urllib.parse.quote_plus(full_address)
    google_maps_url = f"https://www.google.com/maps/dir/?api=1&destination={encoded_destination}"

    tracking = order.get_tracking()
    base_url = get_site_base_url()
    rider_portal_url = f"{base_url}/orders/delivery-partner/{order.id}/?token={tracking.partner_access_token}"
    customer_tracking_url = f"{base_url}/orders/track/{order.id}/"

    items = order.items.all()
    items_html = ""
    items_text = ""
    for item in items:
        subtotal = item.quantity * item.price
        items_html += f"""
        <tr>
            <td style="padding: 10px; border-bottom: 1px solid #e2e8f0; font-weight: 600; color: #1e293b;">{item.product.name}</td>
            <td style="padding: 10px; border-bottom: 1px solid #e2e8f0; text-align: center; color: #475569;">x{item.quantity}</td>
            <td style="padding: 10px; border-bottom: 1px solid #e2e8f0; text-align: right; color: #1e293b; font-weight: 700;">₹{subtotal:.2f}</td>
        </tr>
        """
        items_text += f"- {item.product.name} x{item.quantity} = ₹{subtotal:.2f}\n"

    subject = f"🚨 NEW 10-MIN ORDER #{order.id} (₹{order.total_amount:.2f}) - Deliver to {order.full_name}"

    text_body = f"""
OM SUPER MART — NEW ORDER NOTIFICATION
--------------------------------------------------
Order ID: #{order.id}
Time: {timezone.localtime(order.created_at).strftime('%d %b %Y, %I:%M %p')}
Total Amount: ₹{order.total_amount:.2f}
Payment Method: {payment_method}
Customer PIN: {tracking.delivery_pin}

CUSTOMER DETAILS & DESTINATION:
--------------------------------------------------
Recipient: {order.full_name}
Phone: {order.phone}
Address: {full_address}

GOOGLE MAPS NAVIGATION LINK:
{google_maps_url}

START LIVE DELIVERY / SHARE GPS:
{rider_portal_url}

GROCERY ITEMS TO PACK:
--------------------------------------------------
{items_text}

Total: ₹{order.total_amount:.2f}

Track Live: {customer_tracking_url}
--------------------------------------------------
Om Super Mart Express Fleet
"""

    html_body = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f8fafc; margin: 0; padding: 0; }}
  .container {{ max-width: 600px; margin: 20px auto; background: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.08); }}
  .header {{ background: linear-gradient(135deg, #0c831f 0%, #16a34a 100%); color: #ffffff; padding: 24px; text-align: center; }}
  .badge {{ background: #fef08a; color: #854d0e; font-weight: 800; padding: 4px 12px; border-radius: 999px; font-size: 12px; display: inline-block; }}
  .content {{ padding: 24px; }}
  .card {{ background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 16px; margin-bottom: 20px; }}
  .btn-maps {{ display: block; text-align: center; background: #0c831f; color: #ffffff; text-decoration: none; font-weight: 700; padding: 14px 20px; border-radius: 999px; margin-bottom: 12px; font-size: 15px; }}
  .btn-portal {{ display: block; text-align: center; background: #f1f5f9; color: #0f172a; border: 1.5px solid #cbd5e1; text-decoration: none; font-weight: 700; padding: 12px 20px; border-radius: 999px; font-size: 14px; }}
  .pin-badge {{ font-size: 22px; font-weight: 800; letter-spacing: 4px; color: #0c831f; background: #dcfce7; padding: 6px 16px; border-radius: 8px; display: inline-block; }}
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <div class="badge">⚡ 10-MINUTE EXPRESS DELIVERY</div>
    <h1 style="margin: 12px 0 4px 0; font-size: 24px;">New Order #{order.id} Received!</h1>
    <p style="margin: 0; opacity: 0.9; font-size: 14px;">Total Value: <strong style="font-size: 18px;">₹{order.total_amount:.2f}</strong> ({payment_method})</p>
  </div>

  <div class="content">
    <div class="card">
      <h3 style="margin: 0 0 10px 0; color: #0f172a; font-size: 16px;">📍 Customer & Delivery Destination</h3>
      <p style="margin: 0 0 6px 0; font-size: 15px; color: #1e293b;"><strong>{order.full_name}</strong></p>
      <p style="margin: 0 0 6px 0; font-size: 14px; color: #475569;">📞 Phone: <a href="tel:{order.phone}" style="color: #0c831f; font-weight: 700; text-decoration: none;">{order.phone}</a></p>
      <p style="margin: 0 0 12px 0; font-size: 14px; color: #475569;">🏠 Address: <strong>{full_address}</strong></p>
      <div style="margin-top: 10px;">
        <span style="font-size: 12px; color: #64748b;">Customer PIN to complete:</span><br>
        <span class="pin-badge">{tracking.delivery_pin}</span>
      </div>
    </div>

    <!-- 1-TAP MAPS & RIDER ACTIONS -->
    <div style="margin-bottom: 24px;">
      <a href="{google_maps_url}" class="btn-maps" target="_blank">
        🧭 Open in Google Maps (Start Navigation)
      </a>
      <a href="{rider_portal_url}" class="btn-portal" target="_blank">
        🛵 Open Delivery Partner Portal (Share Live GPS)
      </a>
    </div>

    <div class="card">
      <h3 style="margin: 0 0 12px 0; color: #0f172a; font-size: 16px;">🛒 Items to Pack ({items.count()} items)</h3>
      <table style="width: 100%; border-collapse: collapse; font-size: 14px;">
        <thead>
          <tr style="background: #f1f5f9; color: #64748b; font-size: 12px; text-transform: uppercase;">
            <th style="padding: 8px 10px; text-align: left;">Item</th>
            <th style="padding: 8px 10px; text-align: center;">Qty</th>
            <th style="padding: 8px 10px; text-align: right;">Price</th>
          </tr>
        </thead>
        <tbody>
          {items_html}
        </tbody>
        <tfoot>
          <tr>
            <td colspan="2" style="padding: 12px 10px; font-weight: 700; text-align: right; color: #1e293b;">Final Total:</td>
            <td style="padding: 12px 10px; font-weight: 800; font-size: 16px; text-align: right; color: #0c831f;">₹{order.total_amount:.2f}</td>
          </tr>
        </tfoot>
      </table>
    </div>

    <p style="text-align: center; color: #94a3b8; font-size: 12px; margin-top: 24px;">
      Om Super Mart Express Fleet • Automated Delivery Dispatch Engine
    </p>
  </div>
</div>
</body>
</html>
"""

    try:
        from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "Om Super Mart <noreply@omsupermart.com>")
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_body,
            from_email=from_email,
            to=[owner_email],
        )
        msg.attach_alternative(html_body, "text/html")
        msg.send(fail_silently=True)
        return True
    except Exception as e:
        print(f"Error dispatching owner order notification: {e}")
        return False


def send_customer_order_confirmation(order, payment_method="Online Payment"):
    """Sends receipt & live tracking link to the customer if an email is on file"""
    if not order.user.email:
        return False

    base_url = get_site_base_url()
    tracking_url = f"{base_url}/orders/track/{order.id}/"
    tracking = order.get_tracking()

    subject = f"🎉 Order #{order.id} Confirmed — Om Super Mart 10-Min Delivery"
    text_body = f"""
Hello {order.full_name},

Thank you for shopping with Om Super Mart! Your order has been confirmed and is being packed.

Order #{order.id}
Total: ₹{order.total_amount:.2f} ({payment_method})
Delivery PIN: {tracking.delivery_pin}

Track your order in real time:
{tracking_url}

Your delivery partner Damodar Vaishnav will deliver your order in 10-15 minutes.
"""

    try:
        from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "Om Super Mart <noreply@omsupermart.com>")
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_body,
            from_email=from_email,
            to=[order.user.email],
        )
        msg.send(fail_silently=True)
        return True
    except Exception as e:
        print(f"Customer confirmation email error: {e}")
        return False

