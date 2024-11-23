from user_agents import parse

def get_device_info(request):
    from user_agents import parse

    user_agent_string = request.META.get('HTTP_USER_AGENT', 'Unknown device')
    user_agent = parse(user_agent_string)

    # Extract meaningful details
    browser = f"{user_agent.browser.family} {user_agent.browser.version_string}"
    os = f"{user_agent.os.family} {user_agent.os.version_string}"
    
    # Handle "Unknown Device" fallback
    if user_agent.is_mobile:
        device = "Mobile Device"
    elif user_agent.is_tablet:
        device = "Tablet Device"
    elif user_agent.is_pc:
        device = "Desktop/Laptop"
    else:
        device = "Unknown Device"

    return f"{device} ({os}) using {browser}"
