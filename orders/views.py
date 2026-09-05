import json
import math
from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse

from coupons.models import Coupon
from cart.models import Cart
from inventory.models import InventoryHistory
from .models import Order, OrderItem, OrderDeliveryTracking
from .forms import CheckoutForm

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

@login_required
def checkout(request):

    cart_items = Cart.objects.filter(user=request.user)

    if not cart_items.exists():
        messages.warning(
            request,
            "Your shopping cart is empty. Please add items before checking out."
        )
        return redirect("cart:index")

    total = sum(item.total_price for item in cart_items)

    discount = Decimal("0.00")

    coupon_id = request.session.get("coupon_id")

    if coupon_id:

        try:
            coupon = Coupon.objects.get(id=coupon_id)

            if total >= coupon.minimum_order_amount:

                discount = (
                    total *
                    Decimal(coupon.discount_percent)
                ) / Decimal("100")

        except Coupon.DoesNotExist:
            pass

    final_total = max(Decimal("0.00"), total - discount)

    if request.method == "POST":

        form = CheckoutForm(request.POST)

        if form.is_valid():

            order = Order.objects.create(

                user=request.user,

                full_name=form.cleaned_data["full_name"],

                phone=form.cleaned_data["phone"],

                address=form.cleaned_data["address"],

                city=form.cleaned_data["city"],

                state=form.cleaned_data["state"],

                pincode=form.cleaned_data["pincode"],

                total_amount=final_total

            )

            for item in cart_items:

                OrderItem.objects.create(

                    order=order,

                    product=item.product,

                    quantity=item.quantity,

                    price=item.product.final_price

                )

            cart_items.delete()

            return redirect(
                "payments:payment",
                order.id
            )

    else:

        form = CheckoutForm()

    return render(
        request,
        "orders/checkout.html",
        {
            "form": form,
            "cart_items": cart_items,
            "subtotal": total,
            "total": final_total,
            "discount": discount,
        }
    )


@login_required
def success(request, order_id):

    order = Order.objects.get(
        id=order_id,
        user=request.user
    )

    return render(
        request,
        "orders/order_success.html",
        {
            "order": order
        }
    )


@login_required
def my_orders(request):

    orders = Order.objects.filter(
        user=request.user
    ).order_by("-created_at")

    return render(
        request,
        "orders/my_orders.html",
        {
            "orders": orders
        }
    )


@login_required
def order_detail(request, order_id):

    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    return render(
        request,
        "orders/order_detail.html",
        {
            "order": order
        }
    )

@login_required
def download_invoice(request, order_id):

    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="Om_Super_Mart_Invoice_{order.id}.pdf"'
    )

    doc = SimpleDocTemplate(
        response,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Custom Typography Styles
    brand_title = ParagraphStyle(
        "FM_BrandTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=24,
        leading=28,
        textColor=colors.HexColor("#B91C1C"),
    )
    brand_tagline = ParagraphStyle(
        "FM_BrandTagline",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#64748B"),
    )
    company_info = ParagraphStyle(
        "FM_CompanyInfo",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7.5,
        leading=11,
        textColor=colors.HexColor("#475569"),
    )
    invoice_heading = ParagraphStyle(
        "FM_InvoiceHeading",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        alignment=2,
        textColor=colors.HexColor("#7F1D1D"),
    )
    invoice_meta = ParagraphStyle(
        "FM_InvoiceMeta",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=13,
        alignment=2,
        textColor=colors.HexColor("#334155"),
    )
    card_title = ParagraphStyle(
        "FM_CardTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#B91C1C"),
    )
    card_text = ParagraphStyle(
        "FM_CardText",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=12,
        textColor=colors.HexColor("#1E293B"),
    )
    th_style = ParagraphStyle(
        "FM_TH",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11,
        textColor=colors.white,
    )
    tb_style = ParagraphStyle(
        "FM_TB",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#1E293B"),
    )
    tb_bold = ParagraphStyle(
        "FM_TBBold",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#0F172A"),
    )
    footer_text = ParagraphStyle(
        "FM_Footer",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7.5,
        leading=11,
        alignment=1,
        textColor=colors.HexColor("#64748B"),
    )

    elements = []

    # 1. HEADER ROW: Brand on Left, Tax Invoice on Right
    left_header = [
        Paragraph("Om Super Mart", brand_title),
        Paragraph("10-MINUTE EXPRESS GROCERY DELIVERY", brand_tagline),
        Spacer(1, 4),
        Paragraph("Om Super Mart Retail Private Limited", company_info),
        Paragraph("GSTIN: 27AABCF1234M1Z5 | FSSAI Lic: 11521034000123", company_info),
        Paragraph("Support: support@omsupermart.com | Helpline: +91 902205XXXX", company_info),
        Paragraph("Main Ring Road Hub, Indore, Madhya Pradesh 452001", company_info),
    ]

    right_header = [
        Paragraph("TAX INVOICE", invoice_heading),
        Spacer(1, 4),
        Paragraph(f"<b>Invoice No:</b> OM-INV-2026-{order.id:05d}", invoice_meta),
        Paragraph(f"<b>Date:</b> {order.created_at.strftime('%d %b %Y, %I:%M %p')}", invoice_meta),
        Paragraph(f"<b>Order Ref:</b> #{order.id}", invoice_meta),
        Paragraph("<b>Payment Status:</b> <font color='#16a34a'>PAID / CONFIRMED</font>", invoice_meta),
    ]

    header_table = Table(
        [[left_header, right_header]],
        colWidths=[310, 210]
    )
    header_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 10))

    # Decorative Emerald Line
    divider = Table([[""]], colWidths=[520], rowHeights=[2.5])
    divider.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#1F7A4D")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
    ]))
    elements.append(divider)
    elements.append(Spacer(1, 12))

    # 2. CUSTOMER & DELIVERY ADDRESS BOX
    cust_box = [
        Paragraph("BILLED TO / CUSTOMER", card_title),
        Spacer(1, 3),
        Paragraph(f"<b>Customer:</b> {order.full_name}", card_text),
        Paragraph(f"<b>Contact:</b> {order.phone}", card_text),
        Paragraph(f"<b>Account:</b> {order.user.username} ({order.user.email})", card_text),
    ]

    delivery_box = [
        Paragraph("DELIVERY DESTINATION", card_title),
        Spacer(1, 3),
        Paragraph(f"<b>Address:</b> {order.address}", card_text),
        Paragraph(f"<b>City:</b> {order.city or 'Pune'}, {order.state or 'MH'} - {getattr(order, 'pincode', '411045') or '411045'}", card_text),
        Paragraph("<b>Fulfillment:</b> 10-Minute Doorstep Express", card_text),
    ]

    address_table = Table(
        [[cust_box, delivery_box]],
        colWidths=[255, 255]
    )
    address_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAF8")),
        ("BOX", (0, 0), (-1, -1), 0.75, colors.HexColor("#CBD5E1")),
        ("INNERGRID", (0, 0), (-1, -1), 0.75, colors.HexColor("#E2E8F0")),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    elements.append(address_table)
    elements.append(Spacer(1, 14))

    # 3. ITEMIZED ITEMS TABLE
    items_data = [
        [
            Paragraph("#", th_style),
            Paragraph("Item Description", th_style),
            Paragraph("Unit Price", th_style),
            Paragraph("Qty", th_style),
            Paragraph("Total (INR)", th_style),
        ]
    ]

    subtotal = Decimal("0.00")
    for idx, item in enumerate(order.items.all(), start=1):
        item_tot = item.subtotal()
        subtotal += item_tot
        unit_price = item_tot / item.quantity if item.quantity else Decimal("0.00")
        items_data.append([
            Paragraph(str(idx), tb_style),
            Paragraph(f"<b>{item.product.name}</b><br/><font size='6.5' color='#64748B'>{item.product.category.name}</font>", tb_style),
            Paragraph(f"Rs. {unit_price:.2f}", tb_style),
            Paragraph(str(item.quantity), tb_style),
            Paragraph(f"<b>Rs. {item_tot:.2f}</b>", tb_bold),
        ])

    items_table = Table(
        items_data,
        colWidths=[30, 240, 85, 50, 115]
    )

    table_style_list = [
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F7A4D")),
        ("ALIGN", (0, 0), (0, -1), "CENTER"),
        ("ALIGN", (2, 0), (-1, -1), "RIGHT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#1F7A4D")),
    ]

    for r in range(1, len(items_data)):
        if r % 2 == 0:
            table_style_list.append(("BACKGROUND", (0, r), (-1, r), colors.HexColor("#F8FAF8")))
        else:
            table_style_list.append(("BACKGROUND", (0, r), (-1, r), colors.white))

    items_table.setStyle(TableStyle(table_style_list))
    elements.append(items_table)
    elements.append(Spacer(1, 10))

    # 4. BILL SUMMARY BLOCK
    discount = Decimal("0.00")
    if subtotal > order.total_amount:
        discount = subtotal - order.total_amount

    summary_data = [
        [Paragraph("Items Subtotal:", tb_style), Paragraph(f"Rs. {subtotal:.2f}", tb_bold)],
    ]
    if discount > 0:
        summary_data.append([
            Paragraph("<font color='#16a34a'>Voucher Discount:</font>", tb_style),
            Paragraph(f"<font color='#16a34a'>- Rs. {discount:.2f}</font>", tb_bold)
        ])
    summary_data.extend([
        [Paragraph("Delivery Charge:", tb_style), Paragraph("<font color='#1F7A4D'><b>FREE</b></font>", tb_style)],
        [Paragraph("Taxes (CGST 2.5% + SGST 2.5%):", tb_style), Paragraph("Included in Price", tb_style)],
        [
            Paragraph("<b>GRAND TOTAL:</b>", ParagraphStyle("FM_GTL", parent=card_title, fontSize=10, textColor=colors.HexColor("#122E20"))),
            Paragraph(f"<b>Rs. {order.total_amount:.2f}</b>", ParagraphStyle("FM_GTA", parent=tb_bold, fontSize=11, textColor=colors.HexColor("#1F7A4D")))
        ]
    ])

    summary_table = Table(
        summary_data,
        colWidths=[150, 115]
    )
    summary_table.setStyle(TableStyle([
        ("ALIGN", (0, 0), (0, -1), "RIGHT"),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LINEBELOW", (0, -1), (-1, -1), 1.5, colors.HexColor("#1F7A4D")),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#E3F2E8")),
    ]))

    payment_note = [
        Paragraph("<b>Payment Confirmation</b>", card_title),
        Spacer(1, 2),
        Paragraph("Method: <b>Online / UPI / NetBanking (Verified)</b>", card_text),
        Paragraph(f"Status: <b>{order.status}</b>", card_text),
        Paragraph("Security: <b>PCI-DSS 256-Bit SSL Encrypted</b>", card_text),
    ]

    wrapper_table = Table(
        [[payment_note, summary_table]],
        colWidths=[255, 265]
    )
    wrapper_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ]))
    elements.append(wrapper_table)
    elements.append(Spacer(1, 22))

    # 5. FOOTER & POLICIES
    elements.append(Paragraph("This is an authentic computer-generated tax invoice and requires no physical signature.", footer_text))
    elements.append(Paragraph("Eligible for instant doorstep return/replacement within 24 hours. Queries: support@omsupermart.com", footer_text))
    elements.append(Spacer(1, 4))
    elements.append(Paragraph("<b>Thank you for choosing Om Super Mart! Have a delicious, healthy day!</b>", ParagraphStyle("FM_TY", parent=footer_text, fontName="Helvetica-Bold", fontSize=8.5, textColor=colors.HexColor("#B91C1C"))))

    doc.build(elements)
    return response


@login_required
def cancel_order(request, order_id):

    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    if order.status in [Order.PENDING, Order.CONFIRMED]:

        # Stock was only deducted when order was CONFIRMED (upon successful payment)
        if order.status == Order.CONFIRMED:
            for item in order.items.all():
                product = item.product
                product.stock += item.quantity
                product.save()

                InventoryHistory.objects.create(
                    product=product,
                    action=InventoryHistory.STOCK_IN,
                    quantity=item.quantity,
                    note=f"Cancelled Order #{order.id}"
                )

            # Instant refund to wallet if paid via FreshCash wallet
            if hasattr(order, "payment") and order.payment:
                if order.payment.razorpay_order_id and order.payment.razorpay_order_id.startswith("wallet_"):
                    if hasattr(request.user, "wallet"):
                        request.user.wallet.refund(
                            amount=order.total_amount,
                            description=f"Refund for cancelled order #{order.id}",
                            reference_id=f"ORDER-{order.id}-REFUND"
                        )
                        messages.info(
                            request,
                            f"₹{order.total_amount} has been instantly refunded to your FreshCash Wallet."
                        )

        order.status = Order.CANCELLED
        order.save()

        messages.success(
            request,
            f"Order #{order.id} has been cancelled successfully."
        )

    else:

        messages.warning(
            request,
            f"Order #{order.id} cannot be cancelled because it is already {order.status.lower()}."
        )

    return redirect("orders:my_orders")


@login_required
def track_order(request, order_id):
    """
    Renders the live interactive delivery tracking map & rider dashboard
    """
    if request.user.is_staff:
        order = get_object_or_404(Order, id=order_id)
    else:
        order = get_object_or_404(Order, id=order_id, user=request.user)

    tracking = order.get_tracking()
    telemetry = tracking.get_live_telemetry()
    items = order.items.select_related("product").all()

    return render(
        request,
        "orders/track.html",
        {
            "order": order,
            "tracking": tracking,
            "telemetry": telemetry,
            "items": items,
        }
    )


@login_required
def order_tracking_api(request, order_id):
    """
    Lightweight JSON endpoint providing real-time rider coordinates and progress
    """
    if request.user.is_staff:
        order = get_object_or_404(Order, id=order_id)
    else:
        order = get_object_or_404(Order, id=order_id, user=request.user)

    tracking = order.get_tracking()
    telemetry = tracking.get_live_telemetry()

    return JsonResponse({
        "status": "success",
        "order_id": order.id,
        "order_status": order.status,
        "stage": telemetry["stage"],
        "stage_title": telemetry["stage_title"],
        "stage_desc": telemetry["stage_desc"],
        "progress": telemetry["progress"],
        "eta_minutes": telemetry["eta_minutes"],
        "rider_lat": telemetry["rider_lat"],
        "rider_lng": telemetry["rider_lng"],
        "dark_store_lat": tracking.dark_store_lat,
        "dark_store_lng": tracking.dark_store_lng,
        "customer_lat": tracking.customer_lat,
        "customer_lng": tracking.customer_lng,
        "dark_store_name": tracking.dark_store_name,
        "dark_store_address": tracking.dark_store_address,
        "rider_name": tracking.rider_name,
        "rider_phone": tracking.rider_phone,
        "rider_vehicle": tracking.rider_vehicle,
        "rider_rating": float(tracking.rider_rating),
        "delivery_pin": tracking.delivery_pin,
        "is_delivered": telemetry["is_delivered"],
        "is_cancelled": telemetry.get("is_cancelled", False),
    })


@login_required
def simulate_tracking_stage(request, order_id, stage):
    """
    Allows shoppers/staff to simulate different delivery stages in real-time
    """
    if request.user.is_staff:
        order = get_object_or_404(Order, id=order_id)
    else:
        order = get_object_or_404(Order, id=order_id, user=request.user)

    tracking = order.get_tracking()
    stage_key = stage.upper()

    valid_stages = {
        "RECEIVED": OrderDeliveryTracking.STAGE_RECEIVED,
        "PACKED": OrderDeliveryTracking.STAGE_PACKED,
        "ON_THE_WAY": OrderDeliveryTracking.STAGE_ON_THE_WAY,
        "ARRIVING": OrderDeliveryTracking.STAGE_ARRIVING,
        "DELIVERED": OrderDeliveryTracking.STAGE_DELIVERED,
        "CANCELLED": OrderDeliveryTracking.STAGE_CANCELLED,
    }

    if stage_key == "RESET":
        tracking.override_stage = None
        tracking.save()
        messages.info(request, "Delivery simulation reset to live real-time clock mode.")
    elif stage_key in valid_stages:
        tracking.override_stage = valid_stages[stage_key]
        tracking.save()

        if stage_key == "DELIVERED" and order.status != Order.DELIVERED:
            order.status = Order.DELIVERED
            order.save()

        messages.success(request, f"Simulation updated to: {valid_stages[stage_key]}")

    if request.headers.get("X-Requested-With") == "XMLHttpRequest" or request.GET.get("format") == "json":
        return JsonResponse({"status": "success", "new_stage": tracking.override_stage})

    return redirect("orders:track", order.id)


@login_required
def update_live_location_api(request, order_id):
    """
    Receives real-time live GPS coordinates from the browser Geolocation API
    (navigator.geolocation) and updates the active order's tracking coordinates.
    """
    if request.user.is_staff:
        order = get_object_or_404(Order, id=order_id)
    else:
        order = get_object_or_404(Order, id=order_id, user=request.user)

    if request.method == "POST":
        try:
            body = json.loads(request.body)
            lat = float(body.get("lat", 0))
            lng = float(body.get("lng", 0))
            accuracy = float(body.get("accuracy", 0))
        except Exception:
            lat = float(request.POST.get("lat", 0))
            lng = float(request.POST.get("lng", 0))
            accuracy = float(request.POST.get("accuracy", 0))

        if lat and lng:
            tracking = order.get_tracking()
            tracking.customer_lat = lat
            tracking.customer_lng = lng
            tracking.save()

            # Calculate geodesic distance using Haversine formula
            R = 6371.0  # Earth radius in km
            dlat = math.radians(tracking.customer_lat - tracking.dark_store_lat)
            dlng = math.radians(tracking.customer_lng - tracking.dark_store_lng)
            a = math.sin(dlat / 2)**2 + math.cos(math.radians(tracking.dark_store_lat)) * math.cos(math.radians(tracking.customer_lat)) * math.sin(dlng / 2)**2
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
            distance_km = round(R * c, 2)

            telemetry = tracking.get_live_telemetry()
            return JsonResponse({
                "status": "success",
                "message": f"Real-time live location updated! Driving distance to Om Super Mart Hub: {distance_km} km.",
                "distance_km": distance_km,
                "customer_lat": tracking.customer_lat,
                "customer_lng": tracking.customer_lng,
                "accuracy": accuracy,
                "telemetry": telemetry
            })

    return JsonResponse({"status": "error", "message": "Invalid GPS coordinates."}, status=400)
