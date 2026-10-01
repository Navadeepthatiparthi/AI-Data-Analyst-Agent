import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, tap } from 'rxjs';

import { ApiService } from './api';


export interface User {
  id: string;
  email: string;
  full_name: string;
}


export interface LoginRequest {
  email: string;
  password: string;
}


export interface RegisterRequest {
  email: string;
  password: string;
  full_name: string;
}


export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: User;
}


@Injectable({
  providedIn: 'root'
})
export class AuthService {

  private readonly tokenKey = 'ai_analyst_access_token';
  private readonly userKey = 'ai_analyst_user';


  constructor(
    private http: HttpClient,
    private api: ApiService
  ) {}


  /*
   * Login
   */

  login(
    request: LoginRequest
  ): Observable<LoginResponse> {

    const url = this.api.buildUrl(
      '/api/auth/login'
    );

    return this.http
      .post<LoginResponse>(
        url,
        request
      )
      .pipe(
        tap(response => {

          sessionStorage.setItem(
            this.tokenKey,
            response.access_token
          );

          sessionStorage.setItem(
            this.userKey,
            JSON.stringify(response.user)
          );

        })
      );
  }


  /*
   * Register a new user.
   */

  register(
    request: RegisterRequest
  ): Observable<User> {

    const url = this.api.buildUrl(
      '/api/auth/register'
    );

    return this.http.post<User>(
      url,
      request
    );
  }


  /*
   * Get the currently stored access token.
   */

  getToken(): string | null {

    return sessionStorage.getItem(
      this.tokenKey
    );

  }


  /*
   * Get the currently logged-in user.
   */

  getStoredUser(): User | null {

    const user = sessionStorage.getItem(
      this.userKey
    );

    if (!user) {
      return null;
    }

    try {

      return JSON.parse(user) as User;

    } catch {

      return null;

    }

  }


  /*
   * Check whether the user is authenticated.
   */

  isAuthenticated(): boolean {

    return !!this.getToken();

  }


  /*
   * Ask the backend who the current user is.
   */

  getCurrentUser(): Observable<User> {

    const url = this.api.buildUrl(
      '/api/auth/me'
    );

    return this.http.get<User>(url);

  }


  /*
   * Logout.
   */

  logout(): void {

    sessionStorage.removeItem(
      this.tokenKey
    );

    sessionStorage.removeItem(
      this.userKey
    );

  }

}