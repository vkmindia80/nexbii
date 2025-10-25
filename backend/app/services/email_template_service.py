"""
Email Template Service with Tenant Branding
Supports custom branded email templates for multi-tenant deployments.
"""

import os
from typing import Optional, Dict, List
from jinja2 import Template
from datetime import datetime


class EmailTemplateService:
    """Service for generating branded email templates"""
    
    # ========== Default Email Templates ==========
    
    @staticmethod
    def get_base_template(tenant_branding: Optional[Dict] = None) -> str:
        """
        Get base HTML email template with tenant branding.
        
        Args:
            tenant_branding: Dict with logo_url, primary_color, etc.
        
        Returns:
            str: Base HTML template
        """
        # Default branding
        branding = {
            "logo_url": tenant_branding.get("logo_url") if tenant_branding else None,
            "logo_dark_url": tenant_branding.get("logo_dark_url") if tenant_branding else None,
            "primary_color": tenant_branding.get("primary_color", "#667eea") if tenant_branding else "#667eea",
            "secondary_color": tenant_branding.get("secondary_color", "#764ba2") if tenant_branding else "#764ba2",
            "accent_color": tenant_branding.get("accent_color", "#3b82f6") if tenant_branding else "#3b82f6",
            "font_family": tenant_branding.get("font_family", "Arial, sans-serif") if tenant_branding else "Arial, sans-serif",
            "company_name": tenant_branding.get("company_name", "NexBII") if tenant_branding else "NexBII"
        }
        
        logo_html = ""
        if branding["logo_url"]:
            logo_html = f'<img src="{branding["logo_url"]}" alt="{branding["company_name"]}" style="max-width: 180px; height: auto; margin-bottom: 10px;" />'
        else:
            logo_html = f'<h1 style="margin: 0; font-size: 28px;">{branding["company_name"]}</h1>'
        
        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{{{{ subject }}}}</title>
            <style>
                body {{
                    font-family: {branding["font_family"]};
                    line-height: 1.6;
                    color: #333;
                    margin: 0;
                    padding: 0;
                    background-color: #f4f4f4;
                }}
                .email-container {{
                    max-width: 600px;
                    margin: 20px auto;
                    background: white;
                    border-radius: 8px;
                    overflow: hidden;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                }}
                .header {{
                    background: linear-gradient(135deg, {branding["primary_color"]} 0%, {branding["secondary_color"]} 100%);
                    color: white;
                    padding: 30px 20px;
                    text-align: center;
                }}
                .header h1 {{
                    margin: 10px 0 0 0;
                    font-size: 24px;
                }}
                .content {{
                    padding: 30px 20px;
                }}
                .button {{
                    display: inline-block;
                    background: {branding["primary_color"]};
                    color: white;
                    padding: 12px 30px;
                    text-decoration: none;
                    border-radius: 6px;
                    margin: 20px 0;
                    font-weight: bold;
                }}
                .button:hover {{
                    background: {branding["secondary_color"]};
                }}
                .footer {{
                    background: #f4f4f4;
                    padding: 20px;
                    text-align: center;
                    font-size: 12px;
                    color: #666;
                }}
                .footer a {{
                    color: {branding["accent_color"]};
                    text-decoration: none;
                }}
            </style>
        </head>
        <body>
            <div class="email-container">
                <div class="header">
                    {logo_html}
                    <h1>{{{{ title }}}}</h1>
                    {{{{ subtitle }}}}
                </div>
                <div class="content">
                    {{{{ body_content }}}}
                </div>
                <div class="footer">
                    <p>© {{{{ year }}}} {branding["company_name"]} | {{{{ footer_text }}}}</p>
                    {{{{ unsubscribe_link }}}}
                </div>
            </div>
        </body>
        </html>
        """
    
    # ========== Welcome Email ==========
    
    @staticmethod
    def generate_welcome_email(
        user_name: str,
        login_url: str,
        tenant_branding: Optional[Dict] = None
    ) -> Dict[str, str]:
        """Generate welcome email for new users"""
        
        base_template = EmailTemplateService.get_base_template(tenant_branding)
        company_name = tenant_branding.get("company_name", "NexBII") if tenant_branding else "NexBII"
        
        body_content = f"""
            <p>Hi {user_name},</p>
            
            <p>Welcome to {company_name}! 🎉</p>
            
            <p>Your account has been successfully created. You can now log in and start exploring powerful analytics and business intelligence features.</p>
            
            <center>
                <a href="{login_url}" class="button">Log In Now</a>
            </center>
            
            <p>If you have any questions or need assistance, please don't hesitate to reach out to our support team.</p>
            
            <p>Best regards,<br>
            The {company_name} Team</p>
        """
        
        template = Template(base_template)
        html_content = template.render(
            subject=f"Welcome to {company_name}!",
            title=f"Welcome to {company_name}!",
            subtitle="<p style='margin: 5px 0 0 0; opacity: 0.9;'>Let's get started</p>",
            body_content=body_content,
            year=datetime.now().year,
            footer_text="Business Intelligence Made Simple",
            unsubscribe_link=""
        )
        
        text_content = f"""
        Welcome to {company_name}!
        
        Hi {user_name},
        
        Your account has been successfully created. You can now log in and start exploring powerful analytics features.
        
        Log in at: {login_url}
        
        Best regards,
        The {company_name} Team
        """
        
        return {
            "subject": f"Welcome to {company_name}!",
            "html": html_content,
            "text": text_content
        }
    
    # ========== Password Reset Email ==========
    
    @staticmethod
    def generate_password_reset_email(
        user_name: str,
        reset_url: str,
        expiry_hours: int,
        tenant_branding: Optional[Dict] = None
    ) -> Dict[str, str]:
        """Generate password reset email"""
        
        base_template = EmailTemplateService.get_base_template(tenant_branding)
        company_name = tenant_branding.get("company_name", "NexBII") if tenant_branding else "NexBII"
        
        body_content = f"""
            <p>Hi {user_name},</p>
            
            <p>We received a request to reset your password for your {company_name} account.</p>
            
            <p>Click the button below to reset your password:</p>
            
            <center>
                <a href="{reset_url}" class="button">Reset Password</a>
            </center>
            
            <p><strong>This link will expire in {expiry_hours} hours.</strong></p>
            
            <p>If you didn't request this password reset, please ignore this email or contact support if you have concerns.</p>
            
            <p>Best regards,<br>
            The {company_name} Team</p>
        """
        
        template = Template(base_template)
        html_content = template.render(
            subject="Password Reset Request",
            title="Password Reset",
            subtitle="<p style='margin: 5px 0 0 0; opacity: 0.9;'>Reset your password</p>",
            body_content=body_content,
            year=datetime.now().year,
            footer_text="Security is our priority",
            unsubscribe_link=""
        )
        
        text_content = f"""
        Password Reset Request
        
        Hi {user_name},
        
        We received a request to reset your password for your {company_name} account.
        
        Reset your password: {reset_url}
        
        This link will expire in {expiry_hours} hours.
        
        If you didn't request this, please ignore this email.
        
        Best regards,
        The {company_name} Team
        """
        
        return {
            "subject": "Password Reset Request",
            "html": html_content,
            "text": text_content
        }
    
    # ========== Invitation Email ==========
    
    @staticmethod
    def generate_invitation_email(
        invitee_email: str,
        inviter_name: str,
        organization_name: str,
        invitation_url: str,
        role: str,
        tenant_branding: Optional[Dict] = None
    ) -> Dict[str, str]:
        """Generate invitation email to join tenant"""
        
        base_template = EmailTemplateService.get_base_template(tenant_branding)
        company_name = tenant_branding.get("company_name", "NexBII") if tenant_branding else "NexBII"
        
        body_content = f"""
            <p>Hello,</p>
            
            <p><strong>{inviter_name}</strong> has invited you to join <strong>{organization_name}</strong> on {company_name} as a <strong>{role}</strong>.</p>
            
            <p>Accept the invitation to start collaborating with your team on powerful analytics and dashboards.</p>
            
            <center>
                <a href="{invitation_url}" class="button">Accept Invitation</a>
            </center>
            
            <p>This invitation will expire in 7 days.</p>
            
            <p>If you have any questions, feel free to reply to this email.</p>
            
            <p>Best regards,<br>
            The {company_name} Team</p>
        """
        
        template = Template(base_template)
        html_content = template.render(
            subject=f"You're invited to join {organization_name}",
            title="You're Invited!",
            subtitle=f"<p style='margin: 5px 0 0 0; opacity: 0.9;'>Join {organization_name}</p>",
            body_content=body_content,
            year=datetime.now().year,
            footer_text="Collaboration Made Easy",
            unsubscribe_link=""
        )
        
        text_content = f"""
        You're invited to join {organization_name}
        
        Hello,
        
        {inviter_name} has invited you to join {organization_name} on {company_name} as a {role}.
        
        Accept the invitation: {invitation_url}
        
        This invitation will expire in 7 days.
        
        Best regards,
        The {company_name} Team
        """
        
        return {
            "subject": f"You're invited to join {organization_name}",
            "html": html_content,
            "text": text_content
        }
    
    # ========== Domain Verification Email ==========
    
    @staticmethod
    def generate_domain_verification_email(
        admin_name: str,
        domain: str,
        verification_instructions: Dict,
        tenant_branding: Optional[Dict] = None
    ) -> Dict[str, str]:
        """Generate domain verification instructions email"""
        
        base_template = EmailTemplateService.get_base_template(tenant_branding)
        company_name = tenant_branding.get("company_name", "NexBII") if tenant_branding else "NexBII"
        
        instructions_html = verification_instructions.get("instructions", "").replace("\n", "<br>")
        
        body_content = f"""
            <p>Hi {admin_name},</p>
            
            <p>You've added the custom domain <strong>{domain}</strong> to your {company_name} account.</p>
            
            <p>To verify ownership of this domain, please follow these instructions:</p>
            
            <div style="background: #f8f9fa; padding: 15px; border-left: 4px solid {tenant_branding.get("primary_color", "#667eea") if tenant_branding else "#667eea"}; margin: 20px 0;">
                <p style="margin: 0;"><strong>{verification_instructions.get("title", "Verification Instructions")}</strong></p>
                <p style="margin: 10px 0 0 0; white-space: pre-line;">{instructions_html}</p>
            </div>
            
            <p>Once you've completed these steps, return to your dashboard and click "Verify Domain".</p>
            
            <p>If you need assistance, our support team is here to help.</p>
            
            <p>Best regards,<br>
            The {company_name} Team</p>
        """
        
        template = Template(base_template)
        html_content = template.render(
            subject=f"Verify Your Custom Domain: {domain}",
            title="Domain Verification",
            subtitle=f"<p style='margin: 5px 0 0 0; opacity: 0.9;'>{domain}</p>",
            body_content=body_content,
            year=datetime.now().year,
            footer_text="Custom Domains Made Easy",
            unsubscribe_link=""
        )
        
        text_content = f"""
        Verify Your Custom Domain: {domain}
        
        Hi {admin_name},
        
        You've added the custom domain {domain} to your {company_name} account.
        
        {verification_instructions.get("instructions", "")}
        
        Once completed, return to your dashboard and click "Verify Domain".
        
        Best regards,
        The {company_name} Team
        """
        
        return {
            "subject": f"Verify Your Custom Domain: {domain}",
            "html": html_content,
            "text": text_content
        }
    
    # ========== Custom Template Rendering ==========
    
    @staticmethod
    def render_custom_template(
        template_html: str,
        variables: Dict,
        tenant_branding: Optional[Dict] = None
    ) -> str:
        """
        Render custom email template with variables.
        
        Args:
            template_html: HTML template with Jinja2 variables
            variables: Dictionary of variables to inject
            tenant_branding: Optional branding to apply
        
        Returns:
            str: Rendered HTML
        """
        try:
            # If tenant branding provided, wrap in base template
            if tenant_branding:
                base_template = EmailTemplateService.get_base_template(tenant_branding)
                template = Template(base_template)
                
                # Inject custom content into body
                variables["body_content"] = template_html
                variables.setdefault("year", datetime.now().year)
                variables.setdefault("footer_text", "Powered by NexBII")
                variables.setdefault("unsubscribe_link", "")
                
                return template.render(**variables)
            else:
                # Render template as-is
                template = Template(template_html)
                return template.render(**variables)
        
        except Exception as e:
            return f"<p>Error rendering template: {str(e)}</p>"
