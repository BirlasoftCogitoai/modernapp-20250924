using Microsoft.EntityFrameworkCore;
using Microsoft.OpenApi.Models;
using Api.Services;
using Api.Infrastructure.Data;
using Api.Infrastructure.Repositories;
using Api.Utils;

var builder = WebApplication.CreateBuilder(args);

// Add services to the container.
builder.Services.AddControllers();
builder.Services.AddDbContext<AppDbContext>(options =>
    options.UseNpgsql(builder.Configuration.GetConnectionString("DefaultConnection")));

builder.Services.AddScoped<IUserRepository, UserRepository>();
builder.Services.AddScoped<IAuthService, AuthService>();
builder.Services.AddScoped<IUserService, UserService>();
builder.Services.AddSingleton<IJwtUtils, JwtUtils>();

builder.Services.AddAuthentication("Bearer")
    .AddJwtBearer("Bearer", options =>
    {
        options.Authority = "https://example.com/";
        options.Audience = "your-api";
    });

builder.Services.AddSwaggerGen(c =>
{
    c.SwaggerDoc("v1", new OpenApiInfo { Title = "API", Version = "v1" });
});

var app = builder.Build();

if (app.Environment.IsDevelopment())
{
    app.UseDeveloperExceptionPage();
}
app.UseHttpsRedirection();
app.UseRouting();
app.UseAuthentication();
app.UseAuthorization();
app.UseSwagger();
app.UseSwaggerUI(c =>
{
    c.SwaggerEndpoint("/swagger/v1/swagger.json", "API V1");
});

app.MapControllers();

app.Run();

using Microsoft.AspNetCore.Mvc;
using Api.Services;
using Api.Models;

namespace Api.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class AuthController : ControllerBase
    {
        private readonly IAuthService _authService;

        public AuthController(IAuthService authService)
        {
            _authService = authService;
        }

        [HttpPost("login")]
        public async Task<IActionResult> Login([FromBody] LoginRequest model)
        {
            var response = await _authService.Authenticate(model);
            if (response == null)
                return BadRequest(new { message = "Username or password is incorrect" });

            return Ok(response);
        }
    }
}

using Microsoft.AspNetCore.Mvc;
using Api.Services;

namespace Api.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class UserController : ControllerBase
    {
        private readonly IUserService _userService;

        public UserController(IUserService userService)
        {
            _userService = userService;
        }

        [HttpGet("{id}")]
        public async Task<IActionResult> GetUser(int id)
        {
            var user = await _userService.GetByIdAsync(id);
            if (user == null)
                return NotFound();

            return Ok(user);
        }

        [HttpPost]
        public async Task<IActionResult> CreateUser([FromBody] UserCreateModel model)
        {
            var user = await _userService.CreateAsync(model);
            return CreatedAtAction(nameof(GetUser), new { id = user.Id }, user);
        }
    }
}

using Api.Models;
using Api.Infrastructure.Repositories;
using Api.Utils;
using Microsoft.Extensions.Configuration;

namespace Api.Services
{
    public class AuthService : IAuthService
    {
        private readonly IUserRepository _userRepository;
        private readonly IJwtUtils _jwtUtils;
        private readonly IConfiguration _configuration;

        public AuthService(IUserRepository userRepository, IJwtUtils jwtUtils, IConfiguration configuration)
        {
            _userRepository = userRepository;
            _jwtUtils = jwtUtils;
            _configuration = configuration;
        }

        public async Task<AuthResponse> Authenticate(LoginRequest model)
        {
            var user = await _userRepository.GetByUsernameAsync(model.Username);
            if (user == null || !BCrypt.Net.BCrypt.Verify(model.Password, user.PasswordHash))
                return null;

            var jwtToken = _jwtUtils.GenerateJwtToken(user);
            return new AuthResponse(user, jwtToken);
        }
    }
}

using Api.Models;
using Api.Infrastructure.Repositories;

namespace Api.Services
{
    public class UserService : IUserService
    {
        private readonly IUserRepository _userRepository;

        public UserService(IUserRepository userRepository)
        {
            _userRepository = userRepository;
        }

        public async Task<User> GetByIdAsync(int id)
        {
            return await _userRepository.GetByIdAsync(id);
        }

        public async Task<User> CreateAsync(UserCreateModel model)
        {
            var user = new User
            {
                Username = model.Username,
                PasswordHash = BCrypt.Net.BCrypt.HashPassword(model.Password)
            };

            await _userRepository.AddAsync(user);
            return user;
        }
    }
}

using Microsoft.EntityFrameworkCore;
using Api.Models;

namespace Api.Infrastructure.Data
{
    public class AppDbContext : DbContext
    {
        public AppDbContext(DbContextOptions<AppDbContext> options) : base(options)
        {
        }

        public DbSet<User> Users { get; set; }
    }
}

using System;
using System.IdentityModel.Tokens.Jwt;
using System.Security.Claims;
using System.Text;
using Microsoft.IdentityModel.Tokens;
using Api.Models;

namespace Api.Utils
{
    public interface IJwtUtils
    {
        string GenerateJwtToken(User user);
    }

    public class JwtUtils : IJwtUtils
    {
        private readonly IConfiguration _configuration;

        public JwtUtils(IConfiguration configuration)
        {
            _configuration = configuration;
        }

        public string GenerateJwtToken(User user)
        {
            var tokenHandler = new JwtSecurityTokenHandler();
            var key = Encoding.ASCII.GetBytes(_configuration.GetSection("JwtSettings:Secret").Value);

            var tokenDescriptor = new SecurityTokenDescriptor
            {
                Subject = new ClaimsIdentity(new[] { new Claim("id", user.Id.ToString()) }),
                Expires = DateTime.UtcNow.AddDays(7),
                SigningCredentials = new SigningCredentials(new SymmetricSecurityKey(key), SecurityAlgorithms.HmacSha256Signature)
            };

            var token = tokenHandler.CreateToken(tokenDescriptor);
            return tokenHandler.WriteToken(token);
        }
    }
}

# Microservices Architecture with .NET 6

This repository contains a microservices-based architecture implemented using .NET 6, catering to scalable, secure, and high-performance requirements.

## Setup Instructions

1. **Clone the repository**

2. **Configure Environment Variables**

   Create an `appsettings.json` file in the root directory and populate it with your configuration settings.

3. **Run with Docker**

   Ensure Docker is installed on your machine. Run the following command to start the services:

4. **Run the Application**

   You can run the application using:

5. **Access the API Documentation**

   Open a web browser and navigate to `http://localhost:5000/swagger` to view the API documentation.

## Dependencies

- .NET 6
- Docker
- PostgreSQL
- Redis
- Swagger

## Testing

Run unit tests using:

version: '3.4'

services:
  api:
    image: api
    build:
      context: .
      dockerfile: src/Api/Dockerfile
    ports:
      - "5000:80"
    environment:
      - ASPNETCORE_ENVIRONMENT=Development
    depends_on:
      - db
      - redis

  db:
    image: postgres
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=yourpassword
      - POSTGRES_DB=yourdatabase
    ports:
      - "5432:5432"

  redis:
    image: redis
    ports:
      - "6379:6379"

{
  "ConnectionStrings": {
    "DefaultConnection": "Host=localhost;Database=yourdatabase;Username=postgres;Password=yourpassword"
  },
  "JwtSettings": {
    "Secret": "YourSuperSecretKeyGoesHere"
  },
  "Logging": {
    "LogLevel": {
      "Default": "Information",
      "Microsoft.AspNetCore": "Warning"
    }
  },
  "AllowedHosts": "*"
}

using Xunit;
using Moq;
using Api.Services;
using Api.Infrastructure.Repositories;
using Api.Utils;
using Api.Models;
using System.Threading.Tasks;

namespace Tests.UnitTests
{
    public class AuthServiceTests
    {
        private readonly Mock<IUserRepository> _userRepositoryMock = new();
        private readonly Mock<IJwtUtils> _jwtUtilsMock = new();

        private readonly AuthService _authService;

        public AuthServiceTests()
        {
            _authService = new AuthService(_userRepositoryMock.Object, _jwtUtilsMock.Object, It.IsAny<IConfiguration>());
        }

        [Fact]
        public async Task Authenticate_WithValidCredentials_ReturnsAuthResponse()
        {
            var user = new User { Id = 1, Username = "test", PasswordHash = BCrypt.Net.BCrypt.HashPassword("password") };
            _userRepositoryMock.Setup(repo => repo.GetByUsernameAsync("test")).ReturnsAsync(user);
            _jwtUtilsMock.Setup(jwt => jwt.GenerateJwtToken(user)).Returns("token");

            var response = await _authService.Authenticate(new LoginRequest { Username = "test", Password = "password" });

            Assert.NotNull(response);
            Assert.Equal("token", response.Token);
        }

        [Fact]
        public async Task Authenticate_WithInvalidCredentials_ReturnsNull()
        {
            _userRepositoryMock.Setup(repo => repo.GetByUsernameAsync("test")).ReturnsAsync((User)null);

            var response = await _authService.Authenticate(new LoginRequest { Username = "test", Password = "password" });

            Assert.Null(response);
        }
    }
}