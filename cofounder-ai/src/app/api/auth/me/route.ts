import { NextRequest, NextResponse } from "next/server";
import { cookies } from "next/headers";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

export async function GET(request: NextRequest) {
  try {
    const cookieStore = await cookies();
    const token = cookieStore.get("auth_token");

    if (!token) {
      return NextResponse.json(
        { error: "Not authenticated" },
        { status: 401 }
      );
    }

    // Get user info from backend
    const userRes = await fetch(`${BACKEND_URL}/auth/me`, {
      headers: {
        Authorization: `Bearer ${token.value}`,
      },
    });

    if (!userRes.ok) {
      return NextResponse.json(
        { error: "Invalid token" },
        { status: 401 }
      );
    }

    const userData = await userRes.json();

    // Get company info
    const companyRes = await fetch(`${BACKEND_URL}/companies/me`, {
      headers: {
        Authorization: `Bearer ${token.value}`,
      },
    });

    let company = null;
    if (companyRes.ok) {
      company = await companyRes.json();
    }

    return NextResponse.json({
      email: userData.email,
      company: company,
      hasCompany: !!company,
    });
  } catch (error) {
    console.error("Get me error:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}
