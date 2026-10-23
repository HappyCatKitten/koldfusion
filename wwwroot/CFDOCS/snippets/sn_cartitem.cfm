<!---
    sn_cartitem.cfm - child tag used by the CFASSOCIATE example.
    Produces no output; it just hands its attributes to the enclosing CF_SN_CART.
--->
<CFIF NOT IsDefined("ThisTag.ExecutionMode")>
  This template is a custom tag. Run the CFASSOCIATE example to see it at work.
  <CFABORT>
</CFIF>
<CFPARAM NAME="Attributes.Qty" DEFAULT="1">
<CFPARAM NAME="Attributes.Price" DEFAULT="0">
<CFASSOCIATE BASETAG="CF_SN_CART">
