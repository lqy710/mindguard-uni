package com.mental.controller;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.mental.common.result.Result;
import com.mental.dto.UserUpdateDTO;
import com.mental.service.UserService;
import com.mental.vo.UserStatsVO;
import com.mental.vo.UserVO;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@Tag(name = "用户接口")
@RestController
@RequestMapping("/api/user")
@RequiredArgsConstructor
public class UserController {
    
    private final UserService userService;
    
    @Operation(summary = "获取用户统计数据")
    @GetMapping("/stats")
    public Result<UserStatsVO> getUserStats() {
        return Result.success(userService.getUserStats());
    }
    
    @Operation(summary = "获取用户信息")
    @GetMapping("/{id}")
    public Result<UserVO> getById(@PathVariable Long id) {
        return Result.success(userService.getById(id));
    }
    
    @Operation(summary = "更新个人信息")
    @PutMapping("/profile")
    public Result<UserVO> updateProfile(@RequestBody UserUpdateDTO dto) {
        return Result.success(userService.updateProfile(dto));
    }
    
    @Operation(summary = "获取用户列表(管理员)")
    @GetMapping("/admin/page")
    public Result<Page<UserVO>> getPage(
            @RequestParam(defaultValue = "1") Integer current,
            @RequestParam(defaultValue = "10") Integer size,
            @RequestParam(required = false) String keyword,
            @RequestParam(required = false) Integer status) {
        return Result.success(userService.getPage(current, size, keyword, status));
    }
    
    @Operation(summary = "更新用户状态(管理员)")
    @PutMapping("/admin/{id}/status")
    public Result<Void> updateStatus(@PathVariable Long id, @RequestParam Integer status) {
        userService.updateStatus(id, status);
        return Result.success();
    }
}
