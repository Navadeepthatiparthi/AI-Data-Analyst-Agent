import { CommonModule } from '@angular/common';

import {
  Component
} from '@angular/core';

import {
  FormsModule
} from '@angular/forms';

import {
  Router,
  RouterLink
} from '@angular/router';

import {
  AuthService
} from '../../services/auth.service';


@Component({
  selector: 'app-login',

  standalone: true,

  imports: [
    CommonModule,
    FormsModule,
    RouterLink
  ],

  templateUrl: './login.html',

  styleUrl: './login.css'
})
export class LoginComponent {

  email = '';

  password = '';

  loading = false;

  errorMessage = '';

  /*
   * Controls password visibility.
   */
  showPassword = false;


  constructor(
    private authService: AuthService,
    private router: Router
  ) {}


  /*
   * Show / hide password.
   */
  togglePassword(): void {

    this.showPassword =
      !this.showPassword;

  }


  /*
   * Login.
   */
  login(): void {

    this.errorMessage = '';


    if (
      !this.email.trim() ||
      !this.password
    ) {

      this.errorMessage =
        'Please enter your email and password.';

      return;

    }


    this.loading = true;


    this.authService
      .login({
        email: this.email.trim(),
        password: this.password
      })
      .subscribe({

        next: () => {

          this.loading = false;

          this.router.navigate([
            '/dashboard'
          ]);

        },


        error: error => {

          console.error(
            'Login error:',
            error
          );

          this.loading = false;

          this.errorMessage =
            error?.error?.detail ||
            'Unable to sign in. Please check your credentials.';

        }

      });

  }

}